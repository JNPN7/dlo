import uuid

from typing import List, Optional

from pydantic import Field

from dlo.common.schema import EnumBase, SchemaBase

# =========================
# Enums
# =========================


class ResourceTypes(EnumBase):
    source = "source"
    model = "model"
    relationship = "relationship"
    metric = "metric"


class ColumnCategory(EnumBase):
    dimension = "dimension"
    measure = "measure"


class StorageType(EnumBase):
    table = "table"
    csv = "csv"


class ModelType(EnumBase):
    materialized = "materialized"
    view = "view"
    ephemeral = "ephemeral"
    # incremental = "incremental" 


# =========================
# Base Models
# =========================


class BaseResource(SchemaBase):
    name: str
    file_path: str
    resource_type: ResourceTypes
    description: str
    tags: Optional[List[str]] = None
    uuid: str = Field(default_factory=lambda: str(uuid.uuid4()))


# =========================
# Shared Models
# =========================

class ProfilingMetrics(SchemaBase):
    count: Optional[int] = None
    null_count: Optional[int] = None
    distinct_count: Optional[int] = None


class Column(SchemaBase):
    name: str
    type: str
    category: Optional[ColumnCategory] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    profiling_metrics: Optional[ProfilingMetrics] = None
    sample_data: Optional[List[str | int | float]] = None


# =========================
# Source Models
# =========================

class SourceDetails(SchemaBase):
    full_name: str
    type: StorageType


class Source(BaseResource):
    name: str
    resource_type: ResourceTypes = ResourceTypes.source
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    details: SourceDetails
    connection: Optional[str] = None
    primary_key: Optional[List[str]] = None
    unique_keys: Optional[List[List[str]]] = None
    columns: List[Column]


# =========================
# Model (Semantic / Transform)
# =========================

class ModelDetails(SchemaBase):
    full_name: str
    type: StorageType


class Model(BaseResource):
    name: str
    resource_type: ResourceTypes = ResourceTypes.model
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    type: ModelType
    details: Optional[ModelDetails] = None
    schedule: Optional[str] = None
    primary_key: Optional[List[str]] = None
    unique_keys: Optional[List[List[str]]] = None
    columns: List[Column]


# =========================
# Relationships
# =========================

class Relationship(BaseResource):
    name: str
    resource_type: ResourceTypes = ResourceTypes.relationship
    from_: str = Field(..., alias="from")
    to: str
    from_columns: List[str]
    to_columns: List[str]
    description: Optional[str] = None


# =========================
# Metrics
# =========================

class Metric(BaseResource):
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

