from dataclasses import dataclass, field
from enum import auto
from typing import Optional

from quartz_cron_checker import QuartzCronChecker

from dlo.common.exceptions import errors
from dlo.common.schema import EnumBase, SchemaMixin

# =========================
# Enums
# =========================


class NodeResourceTypes(EnumBase):
    source = auto()
    model = auto()


class ResourceTypes(EnumBase):
    relationship = auto()
    metric = auto()
    source = NodeResourceTypes.source
    model = NodeResourceTypes.model
    code = auto()


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


class CodeType(EnumBase):
    sql = auto()


# =========================
# Base Models
# =========================


@dataclass(kw_only=True)
class BaseResource(SchemaMixin):
    name: str
    file_path: str
    resource_type: ResourceTypes
    description: str
    tags: Optional[list[str]] = field(default=None)
    unique_id: Optional[str] = field(default=None)

    # HACK: Having unique_id same as name. It may change for future requirements
    def __post_init__(self):
        if self.unique_id is None:
            self.unique_id = self.name


# =========================
# Model Mixins
# =========================


@dataclass
class DependsOn(SchemaMixin):
    nodes: list[str] = field(default_factory=list)

    def add_node(self, value: str):
        if value not in self.nodes:
            self.nodes.append(value)


@dataclass
class InjectedCTE(SchemaMixin):
    id: str
    sql: str


@dataclass
class CompiledResourceMixin(SchemaMixin):
    sources: list[str] = field(default_factory=list)
    compiled_path: Optional[str] = field(default=None)
    compiled_code: Optional[str] = field(default=None)
    compiled: bool = field(default=False)
    depends_on: DependsOn = field(default_factory=DependsOn)
    # contains ctes for all dependents
    extra_ctes: list[InjectedCTE] = field(default_factory=list)


@dataclass
class ScheduledResourceMixin(SchemaMixin):
    schedule_depends_on: DependsOn = field(default_factory=DependsOn)

# =========================
# Shared Models
# =========================


@dataclass
class ProfilingMetrics(SchemaMixin):
    count: Optional[int] = field(default=None)
    null_count: Optional[int] = field(default=None)
    distinct_count: Optional[int] = field(default=None)


@dataclass
class Column(SchemaMixin):
    name: str
    type: str
    category: Optional[ColumnCategory] = field(default=None)
    description: Optional[str] = field(default=None)
    tags: Optional[list[str]] = field(default=None)
    profiling_metrics: Optional[ProfilingMetrics] = field(default=None)
    sample_data: Optional[list[str | int | float]] = field(default=None)


# =========================
# Source Models
# =========================


@dataclass
class SourceDetails(SchemaMixin):
    full_name: str
    type: StorageType = field(default=StorageType.table)


@dataclass(kw_only=True)
class Source(BaseResource):
    name: str
    details: SourceDetails
    columns: list[Column] = field(default_factory=list)
    resource_type: ResourceTypes = field(default=ResourceTypes.source)
    description: Optional[str] = field(default=None)
    tags: Optional[list[str]] = field(default=None)
    connection: Optional[str] = field(default=None)
    primary_key: Optional[list[str]] = field(default=None)
    unique_keys: Optional[list[list[str]]] = field(default=None)

    @property
    def relation_name(self):
        return self.details.full_name


# =========================
# Model (Semantic / Transform)
# =========================


@dataclass
class ModelDetails(SchemaMixin):
    full_name: Optional[str] = field(default=None)
    type: StorageType = field(default=StorageType.table)


@dataclass(kw_only=True)
class Model(BaseResource, CompiledResourceMixin, ScheduledResourceMixin):
    name: str
    type: ModelType
    columns: list[Column] = field(default_factory=list)
    resource_type: ResourceTypes = field(default=ResourceTypes.model)
    description: Optional[str] = field(default=None)
    tags: Optional[list[str]] = field(default=None)
    details: Optional[ModelDetails] = field(default=None)
    schedule: Optional[str] = field(default=None)
    primary_key: Optional[list[str]] = field(default=None)
    unique_keys: Optional[list[list[str]]] = field(default=None)
    raw_code: Optional[str] = field(default=None)
    code_path: Optional[str] = field(default=None)

    def __post_init__(self):
        super().__post_init__()

        # Validate schedule cron
        if self.schedule is not None:
            if self.type != ModelType.materialized:
                raise errors.DloCompilationError(
                    f"Only materiazlied model can be scheduled. Invalid Model: `{self.name}` file: `{self.file_path}`"  # noqa: E501
                )
            err_msg = f"Invalid cron expression for Model: `{self.name}` file: `{self.file_path}`"
            try:
                cron_checker = QuartzCronChecker.from_cron_string(self.schedule)
                if not cron_checker.validate():
                    raise errors.DloCompilationError(
                        err_msg
                    )
            except Exception as e:
                raise errors.DloCompilationError(
                    f"{err_msg}\nMessage: {e}"
                )


# =========================
# Relationships
# =========================


@dataclass(kw_only=True)
class Relationship(BaseResource):
    name: str
    from_: str = field(metadata={"alias": "from"})
    to: str
    from_columns: list[str]
    to_columns: list[str]
    resource_type: ResourceTypes = field(default=ResourceTypes.relationship)
    description: Optional[str] = field(default=None)


# =========================
# Metrics
# =========================


@dataclass(kw_only=True)
class Metric(BaseResource):
    name: str
    expression: str
    resource_type: ResourceTypes = field(default=ResourceTypes.metric)
    description: Optional[str] = field(default=None)


# =========================
# Sql
# =========================


@dataclass(kw_only=True)
class Code:
    name: str
    path: str
    code: str
    type: CodeType = field(default=CodeType.sql)


# =========================
# Resource Factory
# =========================


class Resource:
    model_factory = {
        "models": Model,
        "relationships": Relationship,
        "sources": Source,
        "metrics": Metric,
    }

    def create_resource(self, resouce_type: str, data: dict):
        model_cls = self.model_factory.get(resouce_type.lower())
        if not model_cls:
            raise ValueError(f"Resource model: {resouce_type}")
        return model_cls(**data)

    @classmethod
    def get_resource(self, resource_type: str) -> BaseResource:
        return self.model_factory.get(resource_type)
