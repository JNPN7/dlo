from typing import Optional

from dlo.adapters.adapter import Adapter
from dlo.common.schema import SchemaMixin


class DatabricksConfig(SchemaMixin):
    host: str
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    token: Optional[str] = None
    warehouse_id: Optional[str] = None


class DatabricksAdapter(Adapter):
    def __init__(self, config: dict | DatabricksConfig, *args, **kwargs):
        if isinstance(config, DatabricksConfig):
            self.config = config
        else:
            self.config = DatabricksConfig(**config)

    def execute():
        ...
