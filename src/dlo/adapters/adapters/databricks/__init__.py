from dlo.adapters.adapters.databricks.impl import DatabricksAdapter
from dlo.adapters.factory import AdapterFactory


def register(factory: AdapterFactory):
    factory.register("databricks", DatabricksAdapter)
