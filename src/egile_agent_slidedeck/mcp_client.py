"""MCP client for connecting to egile-mcp-slidedeck server."""

from __future__ import annotations

import logging
from typing import Any, Optional
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.sse import sse_client

logger = logging.getLogger(__name__)


class MCPClient:
    """MCP client for communicating with the SlideDeck MCP server."""

    def __init__(
        self,
        transport: str = "sse",
        host: str = "localhost",
        port: int = 8003,
        command: Optional[str] = None,
        timeout: float = 60.0,
    ):
        """
        Initialize the MCP client.

        Args:
            transport: Transport mode - "stdio" or "sse"
            host: Server host (for SSE transport)
            port: Server port (for SSE transport)
            command: Command to start MCP server (for stdio transport)
            timeout: Request timeout in seconds
        """
        self.transport = transport
        self.host = host
        self.port = port
        self.command = command
        self.timeout = timeout
        self.base_url = f"http://{host}:{port}/sse"
        self._session: Optional[ClientSession] = None
        self._exit_stack: Optional[AsyncExitStack] = None

    async def __aenter__(self) -> MCPClient:
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close()

    async def connect(self) -> None:
        """Establish connection to the MCP server."""
        if self._session is not None:
            return
            
        self._exit_stack = AsyncExitStack()
        
        if self.transport == "stdio":
            if not self.command:
                raise ValueError("command is required for stdio transport")
            
            logger.info(f"Starting MCP server via stdio: {self.command}")
            
            import shlex
            command_list = shlex.split(self.command)
            
            server_params = StdioServerParameters(
                command=command_list[0],
                args=command_list[1:],
                env=None
            )
            
            stdio_transport = await self._exit_stack.enter_async_context(
                stdio_client(server_params)
            )
            
            self._session = await self._exit_stack.enter_async_context(
                ClientSession(stdio_transport[0], stdio_transport[1])
            )
            
            await self._session.initialize()
            logger.info("MCP client connected via stdio")
            
        elif self.transport == "sse":
            logger.info(f"Connecting to MCP server at {self.base_url}")
            
            sse_transport = await self._exit_stack.enter_async_context(
                sse_client(self.base_url)
            )
            
            self._session = await self._exit_stack.enter_async_context(
                ClientSession(sse_transport[0], sse_transport[1])
            )
            
            await self._session.initialize()
            logger.info("MCP client connected via SSE")
            
        else:
            raise ValueError(f"Unsupported transport: {self.transport}")

    async def close(self) -> None:
        """Close the connection to the MCP server."""
        if self._exit_stack:
            await self._exit_stack.aclose()
            self._exit_stack = None
            self._session = None
            logger.info("MCP client closed")

    async def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> str:
        """
        Call a tool on the MCP server.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments
            
        Returns:
            Tool response as string
        """
        if not self._session:
            raise RuntimeError("MCP client not connected")
        
        logger.info(f"Calling MCP tool: {tool_name}")
        
        result = await self._session.call_tool(tool_name, arguments=arguments)
        
        # Extract content from result
        if hasattr(result, 'content') and result.content:
            if isinstance(result.content, list) and len(result.content) > 0:
                return result.content[0].text
            elif hasattr(result.content, 'text'):
                return result.content.text
        
        return str(result)
