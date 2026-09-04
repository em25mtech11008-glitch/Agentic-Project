# EDUCATIONAL NOTE:
# This is the actual MCP Server.
# The MCP server is responsible for exposing capabilities (Tools, Resources, Prompts)
# that an MCP client can discover and invoke.
# 
# Think of the MCP server as a standardized interface between the AI application 
# and external capabilities such as APIs, databases, files, or business logic.
# Notice that this server does NOT import LangChain, LangGraph, or Gemini.
# It is completely decoupled from the AI logic itself.

import asyncio
from mcp.server.fastmcp import FastMCP
from typing import Dict, Any

# Import the logic we defined in other modules
from app.mcp.tools import mcp_add, mcp_subtract, mcp_get_weather, mcp_search_documents, mcp_app_info
from app.mcp.resources import get_company_policy, get_rag_metadata
from app.mcp.prompts import get_assistant_prompt, get_summarization_prompt
from app.mcp.mongodb_tools import register_mongodb_tools
from app.mcp.enterprise_tools import register_enterprise_tools

# Initialize the FastMCP server.
# This object manages the lifecycle, routing, and transport (stdio or SSE).
mcp = FastMCP("Company AI MCP Server")

# Register complex tool sets
# Educational Comment:
# We register tool modules in a specific order. MongoDB tools provide the raw
# query capability, while enterprise tools provide the specialized, high-level
# operations that make agents more reliable and faster.
register_mongodb_tools(mcp)
register_enterprise_tools(mcp)

# ==========================================
# 1. Register Tools
# ==========================================
# We use the @mcp.tool decorator to expose Python functions as MCP tools.
# The server will automatically generate JSON Schemas based on the type hints and docstrings.

@mcp.tool()
def add(a: float, b: float) -> float:
    """Adds two numbers."""
    return mcp_add(a, b)

@mcp.tool()
def subtract(a: float, b: float) -> float:
    """Subtracts number b from number a."""
    return mcp_subtract(a, b)

@mcp.tool()
def weather(location: str) -> str:
    """Returns the current weather for a location."""
    return mcp_get_weather(location)

@mcp.tool()
def search_documents(query: str) -> str:
    """Searches the uploaded company documents for the given query."""
    return mcp_search_documents(query)

@mcp.tool()
def app_info() -> str:
    """Returns current application configuration and status."""
    return str(mcp_app_info())

# ==========================================
# 2. Register Resources
# ==========================================
# Resources are registered with a specific URI. 
# When a client requests this URI, the server executes the function and returns the string.

@mcp.resource("config://company/policy")
def company_policy() -> str:
    """The official company policy."""
    return get_company_policy()

@mcp.resource("system://rag/metadata")
def rag_metadata() -> str:
    """Metadata about ingested RAG documents."""
    return get_rag_metadata()

# ==========================================
# 3. Register Prompts
# ==========================================
# Prompts provide reusable instructions to the client.

@mcp.prompt("company_assistant")
def assistant_prompt() -> str:
    """Base system instructions for the company assistant."""
    return get_assistant_prompt()

@mcp.prompt("summarization")
def summarization_prompt() -> str:
    """Prompt specialized for document summarization."""
    return get_summarization_prompt()


if __name__ == "__main__":
    # EDUCATIONAL NOTE:
    # When this script is run directly, mcp.run() starts the server using the standard
    # stdio transport (stdin/stdout). It waits for JSON-RPC messages from a client.
    # We use `python app/mcp/server.py` as the command in our LangGraph client.
    mcp.run()
