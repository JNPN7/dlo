from typing import TYPE_CHECKING

from dlo.agents.tool import ToolRegistry
from dlo.api.contexts import current_manifest

if TYPE_CHECKING:
    from dlo.core.models.manifest import Manifest


def get_tables():
    """Get tables from the semantic layer"""
    manifest: Manifest = current_manifest.get()
    if manifest is None:
        return "Manifest is not loaded"
    tables = []

    for source in manifest.sources.values():
        tables.append(source.name)

    for model in manifest.models.values():
        tables.append(model.name)

    return ", ".join(tables)


def get_schema(table_name: str):
    """Get schema of the specific table"""


def select_table():
    ...


def targeted_entity_search():
    ...


def fewshot_fetcher():
    ...


ToolRegistry.register("get_tables", get_tables)
