from typing import TYPE_CHECKING

from langchain.tools import ToolException, tool
from pydantic import BaseModel, Field

from dlo.agents.tool import ToolRegistry
from dlo.api.contexts import current_manifest, current_profile, current_project
from dlo.core.compiler.runtime import Runtime

if TYPE_CHECKING:
    from dlo.core.config import Profile, Project
    from dlo.core.models.manifest import Manifest


###########################################################
# FIXME: Added here for testing
# Same function is is in dlo.api.routes.charts, Try to move code in core

_query_cache: dict[str, list] = {}


def cached_fetch_data(sql: str, runtime):
    if sql not in _query_cache:
        _query_cache[sql] = runtime.execute_query(sql).to_list()
    return _query_cache[sql]


def inject_data(
    obj: dict, data_map: dict[str, list], lookup: str = "data_key", target: str = "data"
):
    if isinstance(obj, dict):
        if lookup in obj:
            obj[target] = data_map.get(obj[lookup], [])

        for value in obj.values():
            inject_data(value, data_map, lookup, target)

    elif isinstance(obj, list):
        for item in obj:
            inject_data(item, data_map, lookup, target)

###########################################################


class ExecuteQueryArgs(BaseModel):
    """Input for execute query."""
    query: str = Field(description="Query of the chart")
    echarts_option: str = Field(
        description="Options for the chart to be displayed."
                    "Here data is replaced by key of the query"
    )


@tool()
def chart_generation(query: str, echarts_option: dict) -> dict:
    """Generate chart using echarts"""
    manifest: Manifest = current_manifest.get()
    if manifest is None:
        raise ToolException("Manifest is not loaded")

    project: Project = current_project.get()
    profile: Profile = current_profile.get()
    try:
        runtime = Runtime(project=project, profile=profile, manifest=manifest)
        chart_option = echarts_option

        data = cached_fetch_data(query, runtime)

        inject_data(obj=chart_option, data_map=data)

        return {
            "engine": "echarts",
            "option": chart_option,
        }
    except ToolException:
        raise  # Let LangChain handle it via handle_tool_error
    except Exception as e:
        raise ToolException(f"Query execution error: {e}")


# Send error message to the llm instead of crashing
chart_generation.handle_tool_error = True

ToolRegistry.register("chart_generation", chart_generation)
