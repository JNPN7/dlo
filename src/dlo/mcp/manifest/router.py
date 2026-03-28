from fastmcp import FastMCP

mcp = FastMCP(name="Manifest MCP")


@mcp.tool()
def manifest_restart(service: str) -> str:
    return f"Manifest Restarting {service}"


@mcp.tool()
def manifest_health() -> str:
    return "Manifest OK"
