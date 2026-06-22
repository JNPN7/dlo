from dataclasses import dataclass, field
from typing import Mapping, TypeAlias

from dlo.common.schema import SchemaMixin
from dlo.core.models.graph import NodeId
from dlo.core.models.resources import Model

Node = Model

NodeMap: TypeAlias = Mapping[NodeId, Node]


@dataclass
class RuntimeConfig(SchemaMixin):
    timezone_id: str = field(
        default="Asia/Kathmandu",
    )

    @classmethod
    def from_any(cls, value):
        return value if isinstance(value, cls) else cls(**value)


@dataclass
class QueryResult(SchemaMixin):
    columns: list[str]
    rows: list[tuple]

    def to_records(self) -> list[dict]:
        return [
            dict(zip(self.columns, row))
            for row in self.rows
        ]

    def to_list(self) -> dict[str, list]:
        return {
            col: list(values)
            for col, values in zip(self.columns, zip(*self.rows))
        }
