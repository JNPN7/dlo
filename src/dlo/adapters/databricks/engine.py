import asyncio
import concurrent.futures
import hashlib
import logging
import os
from typing import Callable, Iterator, List, Optional, Tuple

from databricks import sql
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.catalog import CatalogInfo
from databricks.sdk.service.compute import Environment
from databricks.sdk.service.jobs import (
    ConditionTask,
    ConditionTaskOp,
    CronSchedule,
    JobEnvironment,
    PerformanceTarget,
    QueueSettings,
    RunIf,
    SqlTask,
    SqlTaskFile,
    Task,
    TaskDependency,
    JobSettings,
    PauseStatus,
)
from databricks.sdk.service.workspace import ImportFormat
from datakit.core.config import RuntimeConfig
from datakit.core.schema import (
    ColumnProfileModel,
    DatasetsModel,
    GraphQueries,
    IntersectionCountModel,
)
from datakit.execution_engine.databricks.schema import (
    ConnectionConfig,
    DatabricksConfig,
    external_location_codes,
)
from datakit.execution_engine.execution_engine import ExecutionEngine
from datakit.utils.type_adapter import list_type_adapter

logger = logging.getLogger(__name__)


class DatabricksEngine(ExecutionEngine):
    """
    A connector for interacting with Databricks Unity Catalog and Jobs.
    Responsible for executing queries and scheduling jobs.
    """

    def __init__(
        self,
        config: DatabricksConfig,
        runtime_config: Optional[RuntimeConfig] = None,
        redis_client_callback: Optional[Callable] = None,
        token_validity_seconds: int = 3600,
    ):
        """
        Initialize the Databricks connector.

        Args:
            config: Databricks authentication config.
            runtime_config: Operational configuration (paths, IDs, etc.).
                            If None, defaults will be used (for target schema).
            redis_client_callback: Optional Redis client for token caching. [Need to be async redis]
            token_validity_seconds: Validity duration for cached tokens.
        """
        self._config = config
        self._runtime_config = runtime_config or RuntimeConfig()  # Default/Fallback
        self._client = None
        self._redis_client_callback = redis_client_callback
        self._config_hash = hashlib.sha256(
            self._config.model_dump_json().encode()
        ).hexdigest()
        self.token_validity_seconds = token_validity_seconds

    @property
    def client(self) -> WorkspaceClient:
        """Get the underlying WorkspaceClient."""
        if self._client is None:
            config_dict = self._config.to_dict()
            logger.debug("Initializing WorkspaceClient with provided config")
            self._client = WorkspaceClient(**config_dict)
        return self._client

    @property
    def token(self) -> str:
        # If no redis, always create a new token
        if self._redis_client_callback is None:
            token = self.client.tokens.create(lifetime_seconds=3600)
            if token.token_value is None:
                raise ValueError("Failed to create access token")
            return token.token_value

        _redis_key = f"databricks_token:{self._config_hash}"

        # Check Redis for existing token
        async def get_cached_token():
            if self._redis_client_callback is None:
                return
            redis_client = await self._redis_client_callback()
            token_value = await redis_client.get(_redis_key)
            return token_value

        token_value = asyncio.run(get_cached_token())

        # If not found, create a new token and store it
        if token_value is None:
            token = self.client.tokens.create(
                lifetime_seconds=self.token_validity_seconds
            )
            if token.token_value is None:
                raise ValueError("Failed to create access token")

            # Store token in Redis with 1 hour expiration
            async def set_cached_token(token_value: str):
                if self._redis_client_callback is None:
                    return
                redis_client = await self._redis_client_callback()
                await redis_client.setex(
                    _redis_key, self.token_validity_seconds, token_value
                )

            asyncio.run(set_cached_token(token.token_value))
            token_value = token.token_value

        return token_value

    def create_connection(
        self,
        connection_name: str,
        config: ConnectionConfig,
    ):
        raise NotImplementedError

    def update_connection(
        self,
        connection_name: str,
        config: ConnectionConfig,
    ):
        raise NotImplementedError

    def delete_connection(self, connection_name: str):
        raise NotImplementedError

    def list_datasets(
        self,
        connection_name: str,
        prefix: str = "",
        warehouse_id: str | None = None,
    ):
        raise NotImplementedError

    def list_catalogs(self, *args, **kwargs) -> Iterator[CatalogInfo]:
        logger.info("Listing catalogs")
        return self.client.catalogs.list()

    def _get_default_warehouse_id(self) -> str:
        """
        Get the SQL warehouse ID for execution.
        Prioritizes RuntimeConfig, then DatabricksConfig, then queries the workspace.
        """
        # 1. Check RuntimeConfig
        if self._runtime_config.warehouse_id:
            return self._runtime_config.warehouse_id

        # 2. Check DatabricksConfig
        if self._config.warehouse_id:
            return self._config.warehouse_id

        # 3. Discover from Workspace
        logger.debug("Fetching available SQL warehouses")
        warehouses = list(self.client.warehouses.list())

        # Filter for running/starting warehouses if possible, but for now take first valid
        valid_warehouses = [w for w in warehouses if w.id]

        if not valid_warehouses:
            error_msg = (
                "No SQL warehouses available. Please create a SQL warehouse first."
            )
            logger.error(error_msg)
            raise ValueError(error_msg)

        warehouse = valid_warehouses[0]
        if not warehouse.id:
            raise ValueError("Warehouse has no ID")
        logger.info(f"Using discovered warehouse: {warehouse.name} ({warehouse.id})")
        return warehouse.id

    def discover_schema_tables(self, catalog_name: str):
        logger.info(f"Discovering schemas and tables for catalog: {catalog_name}")
        warehouse_id = self._get_default_warehouse_id()

        sql_query = f"SHOW SCHEMAS IN {catalog_name};"
        logger.debug(f"Executing query: {sql_query}")

        data = self.execute(sql_query)

        for schema in data:
            name = schema["databaseName"]
            sql_query = f"SHOW TABLES IN {catalog_name}.{name};"
            logger.debug(f"Executing query: {sql_query}")
            self.client.statement_execution.execute_statement(
                warehouse_id=warehouse_id,
                statement=sql_query,
            )

    def upload_code(self, code: str, remote_path: str):
        """
        Uploads code from a local string to the Databricks workspace.
        """
        import base64
        from pathlib import Path

        logger.info(f"Uploading code to {remote_path}")

        try:
            file_path = Path(remote_path)
            parent_path = file_path.resolve().parent

            data_encoded = base64.b64encode(code.encode("utf-8")).decode()

            logger.debug(f"Creating directory {parent_path.as_posix()}")
            self.client.workspace.mkdirs(parent_path.as_posix())

            logger.debug(f"Importing file to {file_path.as_posix()}")
            self.client.workspace.import_(
                path=file_path.as_posix(),
                content=data_encoded,
                format=ImportFormat.AUTO,
                overwrite=True,
            )
            logger.info("Upload successful")
        except Exception as e:
            logger.error(f"Failed to upload code: {e}")
            raise

    def cancel_run(self, run_id: int):
        self.client.jobs.cancel_run(run_id=run_id)

    def run_job(self, job_id: int, *args, **kwargs):
        return self.client.jobs.run_now(job_id=job_id, *args, **kwargs)

    def job_run_status(self, run_id: int, *args, **kwargs):
        run_data = self.client.jobs.get_run(run_id=run_id, *args, **kwargs)

        if run_data.state is None:
            return "FAILED", run_data
        if run_data.state.result_state is not None:
            return run_data.state.result_state.value, run_data
        if run_data.state.life_cycle_state is not None:
            return run_data.state.life_cycle_state.value, run_data

        return "FAILED", run_data

    def job_update(
        self, job_id: int, *, fields_to_remove: Optional[List[str]] = None, new_settings: Optional[JobSettings] = None
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


        """

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

    def get_table_lineage(self, table_name: str):
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        body = {"table_name": table_name, "include_entity_lineage": True}

        res = self.client.api_client.do(
            "GET", "/api/2.0/lineage-tracking/table-lineage", body=body, headers=headers
        )
        return res

    def get_column_lineage(self, table_name: str, column_name: str):
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        body = {"table_name": table_name, "column_name": column_name}

        res = self.client.api_client.do(
            "GET",
            "/api/2.0/lineage-tracking/column-lineage",
            body=body,
            headers=headers,
        )
        return res

    def lineage(self, name: str):
        # NOTE: Refactored to remove hardcoded debugging vars
        table_lineage = {}
        column_lineage = []
        table_metadata = {}

        requested_table = self.client.tables.get(name)
        table_metadata[name] = {"tableInfo": requested_table.as_dict()}

        table_lineage = self.get_table_lineage(name)

        for col in requested_table.columns or []:
            col_name = col.name
            if col_name is None:
                continue
            col_lineage = self.get_column_lineage(name, col_name)

            column_lineage.append(
                {
                    "table_full_name": name,
                    "column_name": col_name,
                    "lineage": col_lineage,
                }
            )

        # Handle Upstreams
        # Note: 'upstreams' key availability depends on the API response structure
        # Assuming table_lineage is a dict-like object returned by get_table_lineage
        upstreams = (
            table_lineage.get("upstreams", [])
            if isinstance(table_lineage, dict)
            else getattr(table_lineage, "upstreams", [])
        )

        for table in upstreams or []:
            # Depending on if it's a dict or object
            table_info = (
                table.get("tableInfo", {})
                if isinstance(table, dict)
                else getattr(table, "table_info", {})
            )

            # Normalize access
            t_name = table_info.get("name")
            t_catalog = table_info.get("catalog_name")
            t_schema = table_info.get("schema_name")

            if t_name is None or t_catalog is None or t_schema is None:
                continue

            full_table_name = f"{t_catalog}.{t_schema}.{t_name}"
            # Fetch upstream table details
            try:
                table_data = self.client.tables.get(full_table_name)
                table_metadata[full_table_name] = {"tableInfo": table_data.as_dict()}
            except Exception as e:
                logger.warning(
                    f"Could not fetch metadata for upstream table {full_table_name}: {e}"
                )

        return table_lineage, column_lineage, table_metadata

    def table_profile(self, datasets: List[DatasetsModel], asset_ids: List[str]):
        """
        Generates a profile for the specified datasets (tables).

        Args:
            datasets: Full list of available datasets.
            asset_ids: IDs of the specific datasets to profile.
        """
        _datasets = list_type_adapter(datasets, DatasetsModel)
        for dataset in _datasets:
            if dataset.id not in asset_ids:
                continue

            dataset_details = self.get_details_from_dataset(dataset)

            logger.info(
                f"Discovering schemas and tables for catalog: {dataset_details}"
            )
            warehouse_id = self._get_default_warehouse_id()
            source_code = dataset_details.get("source_code")
            if not source_code:
                raise KeyError("Asset details must have source code")

            name, _ = self.get_dataset_name_for_query(dataset, source_code)

            DATABRICKS_HTTP_PATH = f"/sql/1.0/warehouses/{warehouse_id}"

            repeat = 0
            while True:
                token = self.token
                try:
                    with sql.connect(
                        server_hostname=self._config.host,
                        http_path=DATABRICKS_HTTP_PATH,
                        access_token=token,
                    ) as connection:
                        with connection.cursor() as cursor:
                            sql_query = f"""
                                CREATE OR REPLACE TEMP VIEW __ontolite_profile_table AS
                                SELECT * FROM {name}"""

                            cursor.execute(sql_query)
                            # We don't need to fetchall here if we just want metadata
                            # data = cursor.fetchall()

                            sql_query = """DESCRIBE TABLE __ontolite_profile_table"""
                            cursor.execute(sql_query)
                            data = cursor.fetchall()
                            schema = {
                                column["col_name"]: column["data_type"]
                                for column in data or []
                            }
                    break
                except Exception as e:
                    if repeat > 1:
                        raise e
                    repeat += 1

            count = self.query_executor(
                _datasets, f"select count(*) as count from {dataset.name}"
            )
            yield {
                "dataset_id": dataset.id,
                "dataset": dataset.name,
                "dtypes": schema,
                "columns": list(schema.keys()),
                "count": count[0]["count"],
            }

    def _profile_single_column(
        self,
        dataset: DatasetsModel,
        field: str,
        sample_limit: int,
        all_datasets: List[DatasetsModel],
    ) -> dict:
        """
        Helper method to profile a single column.
        Intended to be run in a separate thread.
        """
        distinct_count = None
        null_count = None
        sample_data = None

        # 1. Distinct Count & Null Count
        distinct_count_null_count_query = f"""
        SELECT
            COUNT(DISTINCT `{field}`) AS distinct_count,
            SUM(CASE WHEN `{field}` IS NULL THEN 1 ELSE 0 END) AS null_count
        FROM  {dataset.name}
        """
        try:
            # We must pass the full list of datasets to query_executor so it can resolve any dependencies/names if needed
            data = self.query_executor(all_datasets, distinct_count_null_count_query)
            distinct_count = data[0]["distinct_count"]
            null_count = data[0]["null_count"]
        except Exception as e:
            logger.error(
                f"Error profiling column stats for {dataset.name}.{field}: {e}"
            )

        # 2. Sample Data
        sample_data_query = f"""
        SELECT
            DISTINCT CAST(`{field}` AS STRING) AS sample_values
        FROM {dataset.name}
        WHERE `{field}` IS NOT NULL LIMIT {sample_limit}
        """

        try:
            data = self.query_executor(all_datasets, sample_data_query)
            sample_data = [d["sample_values"] for d in data]
        except Exception as e:
            logger.error(f"Error sampling column {dataset.name}.{field}: {e}")

        return {
            "dataset": dataset.id,
            "column": field,
            "distinct_count": distinct_count,
            "null_count": null_count,
            "sample": sample_data,
        }

    def column_profile(
        self, datasets: List[DatasetsModel], tasks: List[ColumnProfileModel]
    ):
        """
        Profiles specific columns (distinct counts, nulls, samples) in parallel.
        """
        # Ensure client is initialized before spawning threads to avoid race condition on lazy init
        _ = self.client

        _datasets = list_type_adapter(datasets, DatasetsModel)
        dataset_map = {dataset.id: dataset for dataset in _datasets}

        # Flatten the work items: (dataset, field, sample_limit)
        work_items = []
        for task in tasks:
            if task.dataset not in dataset_map:
                logger.warning(
                    f"Dataset {task.dataset} not found in provided datasets."
                )
                continue

            dataset = dataset_map[task.dataset]
            for field in task.fields:
                work_items.append((dataset, field, task.sample_limit))

        results = []
        # Use ThreadPoolExecutor to run tasks in parallel
        # max_workers=20 is a heuristic for I/O bound tasks; adjust as needed
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            future_to_item = {
                executor.submit(
                    self._profile_single_column,
                    dataset,
                    field,
                    sample_limit,
                    _datasets,
                ): (dataset, field)
                for dataset, field, sample_limit in work_items
            }

            for future in concurrent.futures.as_completed(future_to_item):
                dataset, field = future_to_item[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as exc:
                    logger.error(
                        f"Profiling task for {dataset.name}.{field} generated an exception: {exc}"
                    )

        # Yield results as they are collected (or yield the whole list - the original was a generator)
        # To maintain generator behavior while being parallel, we can yield as we complete,
        # but we already collected them in the loop above.
        for res in results:
            yield res

    def intersection_count(
        self, datasets: List[DatasetsModel], tasks: List[IntersectionCountModel]
    ):
        """
        Calculates the intersection count between two datasets on specific fields.
        """
        _datasets = list_type_adapter(datasets, DatasetsModel)
        dataset_map = {dataset.id: dataset for dataset in _datasets}
        for task in tasks:
            left_dataset = dataset_map[task.left_dataset]
            right_dataset = dataset_map[task.right_dataset]

            intersection_count = f"""
            SELECT COUNT(*) AS intersection_count
            FROM (
                SELECT DISTINCT a.`{task.left_field}`
                FROM {left_dataset.name} a
                WHERE EXISTS (
                    SELECT 1
                    FROM {right_dataset.name} b
                    WHERE TRY_CAST(a.`{task.left_field}` AS STRING) = TRY_CAST(b.`{task.right_field}` AS STRING)
                )
            )
            """
            data = self.query_executor(_datasets, intersection_count)

            yield {"intersect_count": data[0]["intersection_count"]}

    def execute(self, query: str, warehouse_id: Optional[str] = None):
        if warehouse_id is None:
            warehouse_id = self._get_default_warehouse_id()

        databricks_http_path = f"/sql/1.0/warehouses/{warehouse_id}"

        repeat = 0
        while True:
            token = self.token
            try:
                with sql.connect(
                    server_hostname=self._config.host,
                    http_path=databricks_http_path,
                    access_token=token,
                ) as connection:
                    with connection.cursor() as cursor:
                        cursor.execute(query)
                        data = cursor.fetchall()
                break
            except Exception as e:
                if repeat > 1:
                    raise e
                repeat += 1

        return data

    def query_executor(
        self,
        datasets: list[DatasetsModel] | list[str],
        query: str,
        warehouse_id: Optional[str] = None,
    ):
        """
        Compile and execute a SQL query using QueryService.

        Uses lazy import to avoid circular dependency at module load time.
        The actual compilation logic lives in core/query_service.py.
        """
        # Lazy import to avoid circular dependency
        from datakit.core.query_service import QueryService

        query_service = QueryService(self)
        return query_service.execute_query(datasets, query, warehouse_id)

    @staticmethod
    def get_dataset_name_for_query_external_location(
        dataset: DatasetsModel,
    ) -> Tuple[str, str]:
        details = DatabricksEngine.get_details_from_dataset(dataset)

        dataset_format = details.get("format", "csv")
        dataset_type = details.get("type", "file")
        path = details["full_path"]

        DUCKDB_FORMAT_FUNCTION_MAP = {
            "csv": "csv",
            "parquet": "parquet",
            "json": "json",
            "delta": "delta",
        }

        read_func = DUCKDB_FORMAT_FUNCTION_MAP[dataset_format]
        extension = dataset_format
        path = (
            path
            if dataset_type == "file" or dataset_format == "delta"
            else f"{path}/**/*.{extension}"
        )
        return (
            f"""{read_func}.`{path}` WITH (
          header = "true",
          inferSchema = "true"
        ) """,
            dataset_format,
        )

    @staticmethod
    def get_dataset_name_for_query_external_connector(
        dataset: DatasetsModel,
    ) -> Tuple[str, str]:
        details = DatabricksEngine.get_details_from_dataset(dataset)

        name: Optional[str] = details.get("name")
        if name is None:
            raise ValueError("Name not found for external connection")
        return name, "table"

    @staticmethod
    def get_dataset_name_for_query(dataset: DatasetsModel, source_code: str):
        if source_code in external_location_codes:
            return DatabricksEngine.get_dataset_name_for_query_external_location(
                dataset
            )

        return DatabricksEngine.get_dataset_name_for_query_external_connector(dataset)

    @staticmethod
    def get_details_from_dataset(dataset: DatasetsModel):
        if dataset.details is None:
            raise ValueError("Materialized and view must have details with name")
        return dataset.details

    def get_name_from_dataset(self, dataset: DatasetsModel):
        dataset_details = self.get_details_from_dataset(dataset)
        full_name = dataset_details.get("name")
        if full_name is None:
            raise ValueError("Materialized and view must have details with name")
        return full_name

    def get_remote_path_dir(self, job_name: str):
        return os.path.join(
            self._runtime_config.workspace_path_prefix,
            self._runtime_config.prefix,
            job_name,
        )

    def upload_freshness_sql(
        self,
        dataset: DatasetsModel,
        job_name: str,
    ):
        remote_path = os.path.join(
            self.get_remote_path_dir(job_name),
            "freshness_check",
            f"{dataset.name}.sql",
        )
        full_name = self.get_name_from_dataset(dataset)

        if dataset.metadata is None or dataset.metadata.freshness is None:
            raise ValueError("Freshness need to there to generate freshness sql")

        full_name_split = full_name.split(".")

        # FIX: Ensure metadata.freshness is used
        sql_query = f"""
        SELECT
            CASE
                WHEN last_altered >= current_timestamp() - INTERVAL {dataset.metadata.freshness}
                THEN 'true'
                ELSE 'false'
            END AS is_updated
        FROM system.information_schema.tables
        WHERE table_catalog = '{full_name_split[0]}'
        AND table_schema = '{full_name_split[1]}'
        AND table_name = '{full_name_split[2]}';
        """
        self.upload_code(code=sql_query, remote_path=remote_path)
        return remote_path

    def get_freshness_check_tasks(
        self,
        query: GraphQueries,
        dataset_map: dict[str, DatasetsModel],
        job_name: str,
        check_freshness_dataset_task_map: dict,
        freshness: Optional[str] = None,
    ):
        warehouse_id = self._get_default_warehouse_id()

        # If no freshness defined, no freshness tasks needed
        if freshness is None:
            return [], {}

        tasks: list[Task] = []

        # Create freshness check tasks for each freshness dependent
        for freshness_dependent in query.freshness_dependents:
            # Skip if already created
            if check_freshness_dataset_task_map.get(freshness_dependent) is not None:
                continue

            freshness_dependent_dataset = dataset_map[freshness_dependent]

            # Define task names
            check_freshness_task_name = (
                f"check_freshness_{freshness_dependent_dataset.name}"
            )
            is_fresh_task_name = f"is_fresh_{freshness_dependent_dataset.name}"

            # Upload freshness SQL
            freshness_sql_remote_path = self.upload_freshness_sql(
                freshness_dependent_dataset, job_name
            )

            # Using configured catalog and schema
            target_schema = self._runtime_config.target_schema

            # Create task for freshness check
            check_freshness_task = Task(
                task_key=check_freshness_task_name,
                sql_task=SqlTask(
                    warehouse_id=warehouse_id,
                    file=SqlTaskFile(path=freshness_sql_remote_path),
                    parameters={
                        "catalog": self._runtime_config.catalog_name,
                        "schema": target_schema,
                    },
                ),
                depends_on=[
                    TaskDependency(task_key=dependent) for dependent in query.dependents
                ],
                run_if=RunIf.AT_LEAST_ONE_SUCCESS
                if query.dependents and len(query.dependents) > 0
                else None,
            )
            tasks.append(check_freshness_task)

            # Create task for condition check
            is_fresh_task = Task(
                task_key=is_fresh_task_name,
                condition_task=ConditionTask(
                    op=ConditionTaskOp.EQUAL_TO,
                    left=f"{{{{tasks.{check_freshness_task_name}.output.first_row.is_updated}}}}",
                    right="true",
                ),
                depends_on=[TaskDependency(task_key=check_freshness_task_name)],
            )
            tasks.append(is_fresh_task)
            check_freshness_dataset_task_map[freshness_dependent] = is_fresh_task_name

        return tasks, check_freshness_dataset_task_map

    def upload_query_sql(
        self,
        query: GraphQueries,
        dataset: DatasetsModel,
        job_name: str,
    ):
        remote_path = os.path.join(
            self._runtime_config.workspace_path_prefix,
            self._runtime_config.prefix,
            job_name,
            f"{dataset.name}.sql",
        )

        # Use config for catalog/schema
        catalog = self._runtime_config.catalog_name
        schema = self._runtime_config.target_schema

        # Added catalog and schema usage
        sql_query = f"""
        USE CATALOG `{catalog}`;
        USE SCHEMA `{schema}`;
        {query.query}
        """
        self.upload_code(code=sql_query, remote_path=remote_path)
        return remote_path

    def get_query_tasks(
        self,
        query: GraphQueries,
        job_name: str,
        dataset: DatasetsModel,
        check_freshness_dataset_task_map: dict,
        freshness: Optional[str],
    ):
        warehouse_id = self._get_default_warehouse_id()

        # Upload query SQL
        query_remote_path = self.upload_query_sql(
            query=query,
            dataset=dataset,
            job_name=job_name,
        )

        # Determine dependents based on freshness requirement
        dependents = (
            query.dependents if freshness is None else query.freshness_dependents
        )

        # Create the main query task
        task = Task(
            task_key=query.node,
            sql_task=SqlTask(
                warehouse_id=warehouse_id,
                file=SqlTaskFile(path=query_remote_path),
                parameters={
                    "catalog": self._runtime_config.catalog_name,
                    "schema": self._runtime_config.target_schema,
                },
            ),
            depends_on=[
                TaskDependency(
                    task_key=check_freshness_dataset_task_map.get(dependent, dependent),
                    outcome="true"
                    if dependent in check_freshness_dataset_task_map
                    else None,
                )
                for dependent in dependents
            ],
            run_if=RunIf.AT_LEAST_ONE_SUCCESS
            if dependents and len(dependents) > 0
            else None,
        )
        return task

    def compile_schedule_job(
        self,
        job_name: str,
        queries: list[GraphQueries],
        dataset_map: dict[str, DatasetsModel],
        cron_expression: Optional[str] = None,
        cron_expression_job_id_map: Optional[dict] = None,
    ):
        """
        Compiles and schedules a job for the given queries.
        Renamed from `compilie_schedule_job`.
        """

        if cron_expression_job_id_map is None:
            cron_expression_job_id_map = {}

        tasks: list[Task] = []
        check_freshness_dataset_task_map = {}

        # Create tasks for each query
        for query in queries:
            dataset = dataset_map[query.node]

            # Create freshness check tasks if needed
            freshness = None
            if dataset.metadata is not None:
                freshness = dataset.metadata.freshness
            freshness_tasks, _check_freshness_dataset_task_map = (
                self.get_freshness_check_tasks(
                    query,
                    dataset_map,
                    job_name,
                    check_freshness_dataset_task_map,
                    freshness,
                )
            )
            # Update the main freshness task map to skip duplicates
            check_freshness_dataset_task_map = {
                **check_freshness_dataset_task_map,
                **_check_freshness_dataset_task_map,
            }

            tasks.extend(freshness_tasks)

            # Create the main query task
            query_task = self.get_query_tasks(
                query=query,
                job_name=job_name,
                dataset=dataset,
                check_freshness_dataset_task_map=check_freshness_dataset_task_map,
                freshness=freshness,
            )
            tasks.append(query_task)

        # Create the job with all tasks
        job_id = self.create_job(
            job_name,
            tasks,
            cron_expression=cron_expression,
            job_id=cron_expression_job_id_map.get(cron_expression),
        )
        return job_id

    def create_job(
        self,
        job_name: str,
        tasks: List[Task],
        cron_expression: Optional[str] = None,
        job_id: Optional[int] = None,
    ):
        created_job_id = job_id

        # set up job environment
        environment_key = "serverless_env"
        environments = [
            JobEnvironment(
                environment_key=environment_key,
                spec=Environment(environment_version="4"),
            )
        ]

        # set up job schedule if cron_expression is provided
        schedule = None
        if cron_expression is not None:
            schedule = CronSchedule(
                quartz_cron_expression=cron_expression,
                timezone_id=self._runtime_config.timezone_id,
                pause_status=PauseStatus.UNPAUSED,
            )

        try:
            if job_id is not None:
                try:
                    logger.info(f"Updaing job {job_name} of id {job_id}")
                    job = self.job_update(
                        job_id=job_id,
                        new_settings=JobSettings(
                            name=job_name,
                            tasks=tasks,
                            schedule=schedule,
                            environments=environments,
                            performance_target=PerformanceTarget.PERFORMANCE_OPTIMIZED,
                        ),
                    )
                except Exception:
                    logger.error(f"Couldn't update the job {job_id} with name {job_name} creating new one")
                    job_id = None

            if job_id is None:
                # create the job
                logger.info(f"Job '{job_name}' creating")
                job = self.client.jobs.create(
                    name=job_name,
                    environments=environments,
                    tasks=tasks,
                    performance_target=PerformanceTarget.PERFORMANCE_OPTIMIZED,
                    queue=QueueSettings(enabled=True),
                    schedule=schedule,
                )
                logger.info(f"Job '{job_name}' created successfully")
                created_job_id = job.job_id
            # else:
            #     logger.info(f"Updaing job {job_name} of id {job_id}")
            #     job = self.client.jobs.update(
            #         job_id=job_id,
            #         new_settings=JobSettings(
            #             tasks=tasks,
            #             schedule=schedule,
            #             environments=environments,
            #         ),
            #     )

        except Exception as e:
            logger.error(f"Failed to create job: {e}")
            raise

        return created_job_id

    def pause_job(self, job_id: int):
        try:
            self.client.jobs.update(
                job_id=job_id,
                new_settings=JobSettings(
                    schedule=CronSchedule(
                        quartz_cron_expression="0 0 0 20 2 ? *", # Expression that never runs
                        timezone_id=self._runtime_config.timezone_id,
                        pause_status=PauseStatus.PAUSED,
                    ),
                ),
            )
            logger.info("Job paused: %s", job_id)
        except Exception as e:
            logger.error("Job did not get paused: %s", e)

    def get_task_runs(self, task_key: str, offset: int = 0, limit: int = 200):
        workspace_id = self._config.workspace_id

        # Adding workspace condition for reducing search space
        workspace_condition = ""
        if workspace_id is not None:
            workspace_condition = f" AND workspace_id = '{workspace_id}' "

        query = f"""
        SELECT
            run_id, 
            period_start_time, 
            period_end_time, 
            execution_duration_seconds, 
            termination_code
        FROM
            system.lakeflow.job_task_run_timeline
        WHERE
            task_key = '{task_key}' 
        {workspace_condition}
        ORDER BY period_start_time DESC LIMIT {limit} OFFSET {offset};
        """
        data = self.execute(query)

        # Converting data to dict (Row to dict)
        data_dict = [d.asDict() for d in data]

        return data_dict

    def get_job_runs(self, job_id: int):
        job_data = self.client.jobs.list_runs(job_id=job_id)
        return job_data
