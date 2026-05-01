import logging

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping, Optional

from databricks import sql
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.compute import Environment
from databricks.sdk.service.jobs import (
    CronSchedule,
    JobEnvironment,
    JobSettings,
    PauseStatus,
    PerformanceTarget,
    QueueSettings,
    RunIf,
    SqlTask,
    SqlTaskFile,
    Task,
    TaskDependency,
)
from databricks.sdk.service.workspace import ImportFormat
from dlo.adapters.adapter import Adapter
from dlo.adapters.model import Node, NodeId, NodeMap, RuntimeConfig
from dlo.common.exceptions import errors
from dlo.common.schema import SchemaMixin
from dlo.core.models.resources import ModelType

log = logging.getLogger(__name__)


@dataclass
class DatabricksConfig(SchemaMixin):
    host: str
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    token: Optional[str] = None
    warehouse_http_path: Optional[str] = None

    @property
    def warehouse_id(self):
        return self.warehouse_http_path.split("/")[-1]

    @property
    def config(self) -> dict:
        fields = (
            "host",
            "client_id",
            "client_secret",
            "token",
        )

        return {field: value for field in fields if (value := getattr(self, field)) is not None}

    @classmethod
    def from_any(cls, value: "DatabricksConfig | Mapping[str, Any]"):
        return value if isinstance(value, cls) else cls(**value)


@dataclass
class DatabricksRuntimeConfig(RuntimeConfig):
    workspace_path: str = field(
        default="/Workspace/dlo/",
    )
    run_if: RunIf = field(default=RunIf.AT_LEAST_ONE_SUCCESS)


class DatabricksAdapter(Adapter):
    MODEL_TYPE_TO_TABLE_TYPE = {
        ModelType.materialized: "TABLE",
        ModelType.view: "VIEW",
    }

    def __init__(
        self,
        config: DatabricksConfig | Mapping[str, Any],
        runtime_config: Optional[DatabricksRuntimeConfig | Mapping[str, Any]] = None,
        *args,
        **kwargs,
    ):
        if runtime_config is None:
            runtime_config = {}

        self.config = DatabricksConfig.from_any(config)
        self.runtime_config = DatabricksRuntimeConfig.from_any(runtime_config)

        self._client = None

    @property
    def client(self) -> WorkspaceClient:
        """Get the underlying WorkspaceClient."""
        if self._client is None:
            log.debug("Initializing WorkspaceClient with provided config")
            self._client = WorkspaceClient(**self.config.config)
        return self._client

    # HACK: The job update was not avalabe in sdk
    def job_update(
        self,
        job_id: int,
        *,
        fields_to_remove: Optional[list[str]] = None,
        new_settings: Optional[JobSettings] = None,
    ):
        """Add, update, or remove specific settings of an existing job. Use the [_Reset_
        endpoint](:method:jobs/reset) to overwrite all job settings.

        :param job_id: int
          The canonical identifier of the job to update. This field is required.
        :param fields_to_remove: List[str] (optional)
          Remove top-level fields in the job settings. Removing nested fields is not supported, except for
          tasks and job clusters (`tasks/task_1`). This field is optional.
        :param new_settings: :class:`JobSettings` (optional)
          The new settings for the job.

          Top-level fields specified in `new_settings` are completely replaced, except for arrays which are
          merged. That is, new and existing entries are completely replaced based on the respective key
          fields, i.e. `task_key` or `job_cluster_key`, while previous entries are kept.

          Partially updating nested fields is not supported.

          Changes to the field `JobSettings.timeout_seconds` are applied to active runs. Changes to other
          fields are applied to future runs only.
        """  # noqa: E501

        body = {}
        if fields_to_remove is not None:
            body["fields_to_remove"] = [v for v in fields_to_remove]
        if job_id is not None:
            body["job_id"] = job_id
        if new_settings is not None:
            body["new_settings"] = new_settings.as_dict()
        headers = {
            "Content-Type": "application/json",
        }
        self.client.api_client.do("POST", "/api/2.2/jobs/reset", body=body, headers=headers)

    def connection(self):
        connection = sql.connect(
            server_hostname=self.config.host,
            http_path=self.config.warehouse_http_path,
            access_token=self.config.token,
        )
        return connection

    def execute(self, query: str):
        try:
            with self.connection() as connection:
                with connection.cursor() as cursor:
                    log.info("Executing query:\n%s", query)
                    cursor.execute(query)
                    data = cursor.fetchall()

        except sql.exc.ServerOperationError as server_err:
            raise server_err

            # Removing unnecessary messages, It's for the llm
            # msg = server_err.message or ""
            # msg = re.sub(r"(?is)\n==\s*sql\s*==[\s\S]*$", "", msg, flags=re.IGNORECASE)
            # raise sql.exc.ServerOperationError(msg)

        return data

    def fetch(self, query: str):
        raise errors.DloFeatureNotImplementedError()

    def _create_table(self, model: Node):
        # NOTE: Used this which is optimized but had it like this
        # so that in future we can support python scripts too
        query = model.compiled_code
        table_type = self.MODEL_TYPE_TO_TABLE_TYPE.get(model.type)
        if table_type is None:
            raise errors.DloRuntimeError(
                f"Model type: `{model.type}` not support for adapter: {self.__class__.__name__}"
            )

        query = f"CREATE OR REPLACE {table_type} {model.details.full_name} as {query}"
        self.execute(query)
        log.info("Model: `%s` uuid: `%s` created", model.name, model.unique_id)

    def create_databricks_job(
        self,
        job_name: str,
        tasks: list[Task],
        cron: Optional[str] = None,
        job_id: Optional[int] = None,
    ) -> int:
        """
        Create or update a Databricks job.

        If job_id is provided, attempts update.
        Falls back to create if update fails.
        """

        environment_key = "serverless_env"

        environments = [
            JobEnvironment(
                environment_key=environment_key,
                spec=Environment(environment_version="4"),
            )
        ]

        schedule = (
            CronSchedule(
                quartz_cron_expression=cron,
                timezone_id=self.runtime_config.timezone_id,
                pause_status=PauseStatus.UNPAUSED,
            )
            if cron
            else None
        )

        job_settings = JobSettings(
            name=job_name,
            tasks=tasks,
            schedule=schedule,
            environments=environments,
            performance_target=PerformanceTarget.PERFORMANCE_OPTIMIZED,
        )

        try:
            # -------------------------
            # Update existing job
            # -------------------------
            if job_id:
                log.info("Updating job `%s` (id=%d)", job_name, job_id)

                try:
                    self.job_update(job_id=job_id, new_settings=job_settings)
                    log.info("Job `%s` updated successfully", job_name)
                    return job_id
                except Exception:
                    log.exception(
                        "Failed to update job `%s` (id=%d). Creating new job.",
                        job_name,
                        job_id,
                    )

            # -------------------------
            # Create new job
            # -------------------------
            log.info("Creating job `%s`", job_name)

            job = self.client.jobs.create(
                name=job_name,
                tasks=tasks,
                schedule=schedule,
                environments=environments,
                performance_target=PerformanceTarget.PERFORMANCE_OPTIMIZED,
                queue=QueueSettings(enabled=True),
            )

            log.info("Job `%s` created successfully (id=%d)", job_name, job.job_id)
            return job.job_id

        except Exception as e:
            log.exception("Failed to create or update job `%s`", job_name)
            raise e

    def upload_script(self, code: str, remote_path: str):
        """
        Uploads code from a local string to the Databricks workspace.
        """
        import base64

        from pathlib import Path

        log.info(f"Uploading code to {remote_path}")

        try:
            file_path = Path(remote_path)
            parent_path = file_path.resolve().parent

            data_encoded = base64.b64encode(code.encode("utf-8")).decode()

            log.debug(f"Creating directory {parent_path.as_posix()}")
            self.client.workspace.mkdirs(parent_path.as_posix())

            log.debug(f"Importing file to {file_path.as_posix()}")
            self.client.workspace.import_(
                path=file_path.as_posix(),
                content=data_encoded,
                format=ImportFormat.AUTO,
                overwrite=True,
            )
            log.info("Upload successful")
        except Exception as e:
            log.error(f"Failed to upload code: {e}")
            raise

    def upload_code(
        self,
        node: Node,
        job_name: str,
    ):
        # TODO: Support for sql only rn. Need to extend
        remote_path = Path(self.runtime_config.workspace_path) / job_name / f"{node.name}.sql"

        self.upload_script(code=node.compiled_code, remote_path=remote_path)

        return remote_path

    def get_node_task(
        self,
        node: Node,
        job_name: str,
    ):
        warehouse_id = self.config.warehouse_id

        # Upload query SQL
        query_remote_path = self.upload_code(
            node=node,
            job_name=job_name,
        )

        # TODO: Support for sql only rn. Need to extend
        # Create the main query task
        task = Task(
            task_key=node.name,
            sql_task=SqlTask(
                warehouse_id=warehouse_id,
                file=SqlTaskFile(path=query_remote_path.as_posix()),
            ),
            depends_on=[
                TaskDependency(
                    task_key=dependent,
                )
                for dependent in node.schedule_depends_on.nodes
            ],
            run_if=self.runtime_config.run_if if len(node.schedule_depends_on.nodes) > 0 else None,
        )
        return task

    def create_job(
        self,
        node_map: NodeMap,
        nodes: list[NodeId],
        job_name: str,
        cron: Optional[str] = None,
        job_info: Optional[dict] = None,
    ) -> dict:
        tasks: list[Task] = []
        if job_info is None:
            job_info = {}

        # Create tasks for each query
        for node_unique_id in nodes:
            node = node_map[node_unique_id]

            # Create the main query task
            query_task = self.get_node_task(
                node=node,
                job_name=job_name,
            )
            tasks.append(query_task)

        # Create the job with all tasks
        job_id = self.create_databricks_job(
            job_name=job_name,
            tasks=tasks,
            cron=cron,
            job_id=job_info.get("job_id"),
        )

        return {
            "job_id": job_id,
        }

    def pause_job(self, job_info: dict, cron: str) -> Optional[dict]:
        job_id = job_info["job_id"]

        try:
            self.client.jobs.update(
                job_id=job_id,
                new_settings=JobSettings(
                    tasks=[],
                    schedule=CronSchedule(
                        quartz_cron_expression=cron,
                        timezone_id=self.runtime_config.timezone_id,
                        pause_status=PauseStatus.PAUSED,
                    ),
                ),
            )
            log.info("Job paused: %s", job_id)

            return job_info
        except Exception as e:
            log.error("Couldn't pause the job `%d`. Error: %s", job_id, e)

            return None
