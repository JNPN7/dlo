from dlo.adapters.factory import AdapterFactory
from dlo.adapters.impl.databricks.impl import DatabricksAdapter


def register(factory: AdapterFactory, name: str = "databricks"):
    factory.register(name, DatabricksAdapter)
