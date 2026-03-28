from dataclasses import dataclass, field

from dlo.common.schema import SchemaMixin
from dlo.core.models.resources import Metric, Model, Relationship, Source


@dataclass
class Manifest(SchemaMixin):
    sources: dict[str, Source] = field(default_factory=dict)
    models: dict[str, Model] = field(default_factory=dict)
    relationships: dict[str, Relationship] = field(default_factory=dict)
    metrics: dict[str, Metric] = field(default_factory=dict)
    sql: dict[str, str] = field(default_factory=dict)
