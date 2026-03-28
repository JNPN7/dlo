from typing import NewType, TypeAlias

from dlo.core.models.resources import Model, Source

Node: TypeAlias = Model | Source

# @dataclass
# class Node(SchemaMixin):
#     """
#     A specific node can be model or a source
#     """
#     resource: Model | Source
#     compiled_path: Optional[str] = field(default=None)
#     compiled_query: Optional[str] = field(default=None)
#

NodeId = NewType("NodeId", str)

NodeMap: TypeAlias = dict[NodeId, Node]
