import os
import asyncio
import httpx
from contextlib import AsyncExitStack
from mcp import ClientSession
from mcp.client.sse import sse_client
from langchain_mcp_adapters.tools import load_mcp_tools

class GlobalMCPClient:
    def __init__(self):
        self.session = None
        self.tools = None
        self.exit_stack = None
        self._lock = asyncio.Lock()

    async def connect(self):
        async with self._lock:
            # If already connected, do nothing
            if self.session:
                return

            exit_stack = AsyncExitStack()
            
            # Use the dedicated Service API Key instead of a user's JWT
            mcp_api_key = os.getenv("MCP_API_KEY", "default-dev-key")
            headers = {"Authorization": f"Bearer {mcp_api_key}"}
            
            sse_transport = await exit_stack.enter_async_context(
                sse_client("http://localhost:8001/sse", headers=headers, timeout=30.0)
            )
            read, write = sse_transport
            session = await exit_stack.enter_async_context(ClientSession(read, write))
            
            await session.initialize()
            tools = await load_mcp_tools(session)
            
            self.session = session
            self.tools = tools
            self.exit_stack = exit_stack

    async def get_tools(self):
        if not self.session:
            await self.connect()
        return self.tools

    async def get_session(self) -> ClientSession:
        if not self.session:
            await self.connect()
        return self.session

    async def disconnect(self):
        if self.exit_stack:
            await self.exit_stack.aclose()
        self.session = None
        self.tools = None
        self.exit_stack = None

mcp_client = GlobalMCPClient()
