"""
MCP server
"""

from fastapi import FastAPI
from fastmcp.utilities.lifespan import combine_lifespans

from dlo.mcp.adapter.router import mcp as adapter_mcp
from dlo.mcp.manifest.router import mcp as manifest_mcp

manifest_app = manifest_mcp.http_app(path="/")
adapter_app = adapter_mcp.http_app(path="/")

mcp = FastAPI(
    name="Multi-endpoint MCP Server",
    lifespan=combine_lifespans(manifest_app.lifespan, adapter_app.lifespan),
)

# Mount each MCP app at different routes
mcp.mount("/manifest", manifest_app)
mcp.mount("/adapter", adapter_app)
