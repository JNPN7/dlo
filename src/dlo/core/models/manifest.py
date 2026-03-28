from pydantic import Field

from dlo.common.schema import SchemaBase
from dlo.core.models.resources import Metric, Model, Relationship, Source


class Manifest(SchemaBase):
    sources: dict[str, Source] = Field(default_factory=dict)
    models: dict[str, Model] = Field(default_factory=dict)
    relationships: dict[str, Relationship] = Field(default_factory=dict) 
    metrics: dict[str, Metric] = Field(default_factory=dict) 
    sql: dict[str, str] = Field(default_factory=dict)
