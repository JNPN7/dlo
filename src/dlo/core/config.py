from dataclasses import dataclass

from dlo.common.schema import SchemaMixin


@dataclass
class Project(SchemaMixin):
    project_name: str
    project_root: str
    # version: str
    # profile: str
    # memory: List[str]


@dataclass
class Engine(SchemaMixin):
    type: str
    config: dict


@dataclass
class Connection(SchemaMixin):
    ...


@dataclass
class Profile(SchemaMixin):
    engine: Engine
    connections: dict[str, Connection]
