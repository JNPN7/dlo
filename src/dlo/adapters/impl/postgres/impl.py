import logging

from dataclasses import dataclass, fields
from typing import Any, ClassVar, Mapping, Optional

import psycopg2

from psycopg2.extras import RealDictCursor

from dlo.adapters.adapter import Adapter
from dlo.adapters.model import Node, NodeId, NodeMap, QueryResult
from dlo.common.exception import errors
from dlo.common.schema import SchemaMixin
from dlo.core.constants import DEFAULT_CURSOR_LIMIT, TMP_MODEL_PREFIX
from dlo.core.models.resources import ModelType

log = logging.getLogger(__name__)


@dataclass
class PostgresConfig(SchemaMixin):
    # Define connection groups once
    URL_FIELDS: ClassVar[set[str]] = {"url"}
    PARAM_FIELDS: ClassVar[set[str]] = {
        "host",
        "port",
        "dbname",
        "user",
        "password",
    }

    host: Optional[str] = None
    port: Optional[str] = None
    dbname: Optional[str] = None
    user: Optional[str] = None
    password: Optional[str] = None
    url: Optional[str] = None

    def __post_init__(self):
        values = {f.name: getattr(self, f.name) for f in fields(self)}

        has_url = any(values[f] is not None for f in self.URL_FIELDS)
        has_params = any(values[f] is not None for f in self.PARAM_FIELDS)

        if has_url and has_params:
            raise ValueError(
                "Provide either 'url' or the individual connection parameters, not both."
            )

        if not has_url:
            missing = [
                f for f in self.PARAM_FIELDS
                if values[f] is None
            ]
            if missing:
                raise ValueError(
                    f"When 'url' is not provided, missing required fields: {', '.join(sorted(missing))}"  # noqa: E501
                )

    @property
    def config(self) -> dict:
        return {
            field: value for field in self.PARAM_FIELDS
            if (value := getattr(self, field)) is not None
        }

    @classmethod
    def from_any(cls, value: "PostgresConfig | Mapping[str, Any]"):
        return value if isinstance(value, cls) else cls(**value)


class PostgresAdapter(Adapter):
    MODEL_TYPE_TO_TABLE_TYPE: ClassVar[Mapping[ModelType, str]] = {
        ModelType.materialized: "TABLE",
        ModelType.view: "VIEW",
    }

    def __init__(
        self,
        config: PostgresConfig | Mapping[str, Any],
        runtime_config: Optional[Mapping[str, Any]] = None,
        *args,
        **kwargs,
    ):
        if runtime_config is None:
            runtime_config = {}

        self.config = PostgresConfig.from_any(config)
        self.runtime_config = runtime_config

    def connection(self):
        if self.config.url is not None:
            log.debug("Using URL postgres config")
            return psycopg2.connect(self.config.url)
        return psycopg2.connect(**self.config.config)

    def execute(self, query: str, cursor_limit: Optional[int] = DEFAULT_CURSOR_LIMIT):
        with self.connection() as connection:
            with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                log.info("Executing query:\n%s", query)
                cursor.execute(query)
                if cursor_limit is None:
                    data = cursor.fetchall()
                else:
                    data = cursor.fetchmany(cursor_limit)
        return data

    def query(self, query: str, cursor_limit: Optional[int] = DEFAULT_CURSOR_LIMIT) -> QueryResult:
        rows = self.execute(query, cursor_limit)
        if not rows:
            return QueryResult(columns=[], rows=[])

        columns = list(rows[0].keys())

        return QueryResult(
            columns=columns,
            rows=[tuple(row.values()) for row in rows],
        )

    def _create_table(self, model: Node):
        # NOTE: Used this which is optimized but had it like this
        # so that in future we can support python scripts too
        query = model.compiled_code
        table_type = self.MODEL_TYPE_TO_TABLE_TYPE.get(model.type)
        if table_type is None:
            raise errors.DloRuntimeError(
                f"Model type: `{model.type}` not support for adapter: {self.__class__.__name__}"
            )

        with self.connection() as connection:
            with connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                full_name = model.details.full_name

                name_parts = full_name.split(".")
                name = name_parts[-1]
                name_parts[-1] = f"{TMP_MODEL_PREFIX}{name}"
                tmp_full_name = ".".join(name_parts)

                cursor.execute("BEGIN")
                try:
                    create_query = f"CREATE {table_type} {tmp_full_name} as {query}"
                    log.info("Creating temporary table for model `%s`", model.name)
                    log.info("Model: %s Create Query: %s", model.name, create_query)
                    cursor.execute(create_query)

                    drop_query = f"DROP {table_type} IF EXISTS {full_name}"
                    log.info("Dropping table of model `%s`", model.name)
                    log.info("Model: %s Dropping Query: %s", model.name, drop_query)
                    cursor.execute(drop_query)

                    rename_query = f"ALTER {table_type} {tmp_full_name} RENAME TO {name}"
                    log.info("Rename temporary table to its original of model `%s`", model.name)
                    log.info("Model: %s Rename Query: %s", model.name, rename_query)
                    cursor.execute(rename_query)

                    cursor.execute("COMMIT")
                    log.info("Model: `%s` uuid: `%s` created", model.name, model.unique_id)
                except Exception as e:
                    log.error(
                        "Model: `%s` uuid: `%s`. Got error while creation: `%s`",
                        model.name, model.unique_id, e
                    )
                    cursor.execute("ROLLBACK")

    def create_job(
        self,
        node_map: NodeMap,
        nodes: list[NodeId],
        job_name: str,
        cron: Optional[str] = None,
        job_info: Optional[dict] = None,
    ) -> dict:
        raise errors.DloFeatureNotImplementedError(
            "Jobs for postgres not implement (Please implement Orchestrator)"
        )

    def pause_job(self, job_info: dict, cron: str) -> Optional[dict]:
        raise errors.DloFeatureNotImplementedError(
            "Jobs for postgres not implement (Please implement Orchestrator)"
        )
