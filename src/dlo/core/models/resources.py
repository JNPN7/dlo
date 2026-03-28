import uuid

from dataclasses import dataclass, field
from enum import auto
from typing import Optional

from dlo.common.schema import EnumBase, SchemaMixin

# =========================
# Enums
# =========================


class ResourceTypes(EnumBase):
    source = auto()
    model = auto()
    relationship = auto()
    metric = auto()


class ColumnCategory(EnumBase):
    dimension = auto()
    measure = auto()


class StorageType(EnumBase):
    table = auto()
    csv = auto()


class ModelType(EnumBase):
    materialized = auto()
    view = auto()
    ephemeral = auto()
    # incremental = auto()


# =========================
# Base Models
# =========================


@dataclass
class BaseResource(SchemaMixin):
    name: str
    file_path: str
    resource_type: ResourceTypes
    description: str
    tags: Optional[list[str]] = None
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))


# =========================
# Shared Models
# =========================

@dataclass
class ProfilingMetrics(SchemaMixin):
    count: Optional[int] = None
    null_count: Optional[int] = None
    distinct_count: Optional[int] = None


@dataclass
class Column(SchemaMixin):
    name: str
    type: str
    category: Optional[ColumnCategory] = None
    description: Optional[str] = None
    tags: Optional[list[str]] = None
    profiling_metrics: Optional[ProfilingMetrics] = None
    sample_data: Optional[list[str | int | float]] = None


# =========================
# Source Models
# =========================

@dataclass
class SourceDetails(SchemaMixin):
    full_name: str
    type: StorageType


@dataclass
class Source(SchemaMixin):
    name: str
    resource_type: ResourceTypes = ResourceTypes.source
    description: Optional[str] = None
    tags: Optional[list[str]] = None
    details: SourceDetails
    connection: Optional[str] = None
    primary_key: Optional[list[str]] = None
    unique_keys: Optional[list[list[str]]] = None
    columns: list[Column]


# =========================
# Model (Semantic / Transform)
# =========================

@dataclass
class ModelDetails(SchemaMixin):
    full_name: str
    type: StorageType


@dataclass
class Model(SchemaMixin):
    name: str
    resource_type: ResourceTypes = ResourceTypes.model
    description: Optional[str] = None
    tags: Optional[list[str]] = None
    type: ModelType
    details: Optional[ModelDetails] = None
    schedule: Optional[str] = None
    primary_key: Optional[list[str]] = None
    unique_keys: Optional[list[list[str]]] = None
    columns: list[Column]


# =========================
# Relationships
# =========================

@dataclass
class Relationship(SchemaMixin):
    name: str
    resource_type: ResourceTypes = ResourceTypes.relationship
    from_: str = field(metadata={"alias": "from"})
    to: str
    from_columns: list[str]
    to_columns: list[str]
    description: Optional[str] = None


# =========================
# Metrics
# =========================

@dataclass
class Metric(SchemaMixin):
    name: str
    resource_type: ResourceTypes = ResourceTypes.metric
    expression: str
    description: Optional[str] = None


# =========================
# Resource Factory
# =========================

class Resource:
    model_factory = {
        'models': Model,
        'relationships': Relationship,
        'sources': Source,
        'metrics': Metric
    }

    def create_resource(self, resouce_type: str, data: dict):
        model_cls = self.model_factory.get(resouce_type.lower())
        if not model_cls:
            raise ValueError(f"Resource model: {resouce_type}")
        return model_cls(**data)

    @classmethod
    def get_resource(self, resource_type: str) -> BaseResource:
        return self.model_factory.get(resource_type)
