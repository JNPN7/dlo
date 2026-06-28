from typing import TYPE_CHECKING

from langchain.tools import ToolException, tool
from pydantic import BaseModel, Field

from dlo.adapters.model import QueryResult
from dlo.agents.tool import ToolRegistry
from dlo.api.contexts import current_manifest, current_profile, current_project
from dlo.core.compiler.runtime import Runtime

if TYPE_CHECKING:
    from dlo.core.config import Profile, Project
    from dlo.core.models.manifest import Manifest


class ExecuteQueryArgs(BaseModel):
    """Input for execute query."""
    query: str = Field(description="Query to be executed")


@tool(args_schema=ExecuteQueryArgs)
def execute_query(query: str) -> QueryResult:
    """Exeucte query and return data"""
    manifest: Manifest = current_manifest.get()
    if manifest is None:
        return "Manifest is not loaded"
    project: Project = current_project.get()
    profile: Profile = current_profile.get()
    try:
        runtime = Runtime(project=project, profile=profile, manifest=manifest)

        result = runtime.execute_query(query, cursor_limit=project.cursor_limit)
        return result
    except ToolException:
        raise  # Let LangChain handle it via handle_tool_error
    except Exception as e:
        raise ToolException(f"Query execution error: {e}")


# Send error message to the llm instead of crashing
execute_query.handle_tool_error = True

ToolRegistry.register("execute_query", execute_query)
