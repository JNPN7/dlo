
import logging

from dataclasses import dataclass
from typing import Any, Mapping, Optional

from databricks import sql
from dlo.adapters.adapter import Adapter
from dlo.common.exceptions import errors
from dlo.common.schema import SchemaMixin
from dlo.core.models.resources import Model, ModelType

log = logging.getLogger(__name__)


@dataclass
class DatabricksConfig(SchemaMixin):
    host: str
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    token: Optional[str] = None
    warehouse_http_path: Optional[str] = None

    @classmethod
    def from_any(cls, value: "DatabricksConfig | Mapping[str, Any]"):
        return value if isinstance(value, cls) else cls(**value)


class DatabricksAdapter(Adapter):
    MODEL_TYPE_TO_TABLE_TYPE = {
        ModelType.materialized: "TABLE",
        ModelType.view: "VIEW",
    }

    def __init__(self, config: DatabricksConfig | Mapping[str, Any], *args, **kwargs):
        self.config = DatabricksConfig.from_any(config)

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
                    cursor.execute(query)
                    data = cursor.fetchall()

        except sql.exc.ServerOperationError as server_err:
            raise server_err

            # Removing unnecessary messages, It's for the llm
            # msg = server_err.message or ""
            # msg = re.sub(r"(?is)\n==\s*sql\s*==[\s\S]*$", "", msg, flags=re.IGNORECASE)
            # raise sql.exc.ServerOperationError(msg)

        return data

    def fetch(self):
        raise errors.DloFeatureNotImplementedError()

    def _create(self, model: Model):
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
