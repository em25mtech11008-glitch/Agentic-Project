# EDUCATIONAL NOTE:
# This is the MCP Client utility.
# We manage a global, persistent connection to the MCP Server.
# This prevents opening and closing subprocesses on every single AI turn,
# which avoids complex anyio TaskGroup scope issues when used within LangGraph.

import os
import asyncio
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools

server_params = StdioServerParameters(
    command=os.path.abspath(os.path.join(".venv", "Scripts", "python.exe")) if os.name == 'nt' else "python",
    args=["-m", "app.mcp.server"],
)

class GlobalMCPClient:
    def __init__(self):
        self.session: ClientSession | None = None
        self.exit_stack = AsyncExitStack()
        self.tools = []
        self._lock = asyncio.Lock()

    async def connect(self):
        """Establish a persistent connection to the MCP server."""
        async with self._lock:
            if self.session is not None:
                return  # Already connected
            
            print("\n[MCP Client] Starting global connection to MCP Server...")
            # We use AsyncExitStack to keep the context managers alive
            # outside of a standard 'async with' block.
            stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
            read, write = stdio_transport
            self.session = await self.exit_stack.enter_async_context(ClientSession(read, write))
            
            await self.session.initialize()
            print("[MCP Client] Initialized successfully. Loading tools...")
            
            # Load tools once globally
            self.tools = await load_mcp_tools(self.session)
            print(f"[MCP Client] Loaded {len(self.tools)} tools.")

    async def get_tools(self):
        """Returns the loaded LangChain tools, connecting if necessary."""
        if self.session is None:
            await self.connect()
        return self.tools

    async def get_session(self) -> ClientSession:
        """Returns the active session."""
        if self.session is None:
            await self.connect()
        return self.session

    async def disconnect(self):
        """Cleans up the connection when shutting down the application."""
        if self.session is not None:
            await self.exit_stack.aclose()
            self.session = None

# Global instance
mcp_client = GlobalMCPClient()
