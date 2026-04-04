from mcp.server.fastmcp import FastMCP

mcp = FastMCP("demo-server")

# Tool: callable action
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two integers."""
    return a + b

# Resource: read-only context
@mcp.resource("demo://hello")
def hello() -> str:
    """A tiny resource you can load into context."""
    return "Hello from MCP resource demo://hello"

if __name__ == "__main__":
    # For Claude Code, stdio is the simplest to start with
    mcp.run(transport="stdio")
