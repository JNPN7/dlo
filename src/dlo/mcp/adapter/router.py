from fastmcp import FastMCP

mcp = FastMCP(name="Adapter MCP")


@mcp.tool()
def adapter_restart(service: str) -> str:
    return f"Adapter Restarting {service}"


@mcp.tool()
def adapter_health() -> str:
    return "Adapter OK"
