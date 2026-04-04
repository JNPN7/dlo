from dlo.adapters.adapters.databricks.impl import DatabricksAdapter
from dlo.adapters.factory import AdapterFactory


def register(factory: AdapterFactory, name: str = "databricks"):
    factory.register(name, DatabricksAdapter)
