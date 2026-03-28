from typing import Optional

from pydantic import BaseModel

external_location_codes = [
    "AZURE_BLOB",
    "S3",
    "GCS",
    "AZURE_DATA_LAKE",
    "adls",
    "s3",
    "gcs",
]


class DatabricksConfig(BaseModel):
    host: str
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    token: Optional[str] = None
    warehouse_id: Optional[str] = None
    workspace_id: Optional[str] = None

    def to_dict(self) -> dict:
        d = {"host": self.host}
        if self.client_id:
            d["client_id"] = self.client_id
        if self.client_secret:
            d["client_secret"] = self.client_secret
        if self.token:
            d["token"] = self.token
        return d


class ConnectionConfig(BaseModel):
    connection_type: str
    auth_type: str
    credentials: dict
    connection_config: dict
