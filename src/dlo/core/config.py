from typing import Dict, List

from dlo.common.schema import SchemaBase


class Project(SchemaBase):
    project_name: str
    version: str
    project_root: str
    profile: str
    memory: List[str]


class Engine(SchemaBase):
    type: str
    config: dict


class Connection(SchemaBase):
    ...


class Profile(SchemaBase):
    engine: Engine
    connections: Dict[str, Connection]
