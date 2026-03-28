from dlo.common.schema import SchemaBase


class Project(SchemaBase):
    project_name: str
    project_root: str