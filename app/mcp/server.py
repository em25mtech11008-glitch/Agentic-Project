import asyncio
from mcp.server.fastmcp import FastMCP
from app.mcp.tools import register_tools

mcp = FastMCP("Company AI MCP Server", port=8001)

# Register all simplified tools
register_tools(mcp)

if __name__ == "__main__":
    mcp.run(transport="sse")
