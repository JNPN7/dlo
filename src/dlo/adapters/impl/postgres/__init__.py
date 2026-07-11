from dlo.adapters.factory import AdapterFactory
from dlo.adapters.impl.postgres.impl import PostgresAdapter


def register(factory: AdapterFactory, name: str = "postgres"):
    factory.register(name, PostgresAdapter)
