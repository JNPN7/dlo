from typing import TYPE_CHECKING, Optional

from langchain.tools import ToolException, tool

from dlo.agents.tool import ToolRegistry
from dlo.api.contexts import current_manifest

if TYPE_CHECKING:
    from dlo.core.models.manifest import Manifest
    from dlo.core.models.resources import Model, Source


def get_manifest():
    manifest: Manifest = current_manifest.get()
    if manifest is None:
        raise ToolException("Manifest is not loaded")
    return manifest


@tool()
def get_tables() -> list[dict]:
    """Get tables from the semantic layer"""
    manifest: Manifest = get_manifest()
    tables = []

    keys = ("name", "description", "tag", "resource_type", "file_path", "type")

    for source in manifest.sources.values():
        tables.append({k: getattr(source, k, None) for k in keys})

    for model in manifest.models.values():
        tables.append({k: getattr(model, k, None) for k in keys})

    return tables


@tool()
def get_schema(table_name: str):
    """Get schema (create statement) of the specific table

    Args:
        table_name: str (Name of table whose schema is requried)
    """
    manifest: Manifest = get_manifest()

    # Given the fact that the key of the source and model is the table name itself
    table: Optional[Source | Model] = (
        manifest.sources.get(table_name)
        or manifest.models.get(table_name)
    )

    if table is None:
        raise ToolException("Table not found")

    table_columns = table.columns
    if not table_columns:
        raise ToolException(
            "Table schema not found. Please run upstream first, meanwhile get schema from query"
        )

    columns = ",\n".join(
        [
            f"{col.name} {col.type} --> {col.category} --> {col.description}"
            for col in table.columns
        ]
    )
    create_statement = f"""CREATE TABLE {table.name} (
        {columns}
    )"""
    return create_statement


def select_table():
    ...


def targeted_entity_search():
    ...


def fewshot_fetcher():
    ...


# Send error message to the llm instead of crashing
get_tables.handle_tool_error = True
get_schema.handle_tool_error = True

ToolRegistry.register("get_tables", get_tables)
ToolRegistry.register("get_schema", get_schema)
