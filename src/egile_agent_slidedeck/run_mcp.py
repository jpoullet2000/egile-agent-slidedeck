"""Run only the MCP server (without AgentOS)."""

from __future__ import annotations

import logging
import os
import sys

from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

load_dotenv()


def run_mcp_only():
    """Run only the MCP server."""
    port = os.getenv("MCP_PORT", "8003")
    host = os.getenv("MCP_HOST", "0.0.0.0")
    
    logger.info("Starting SlideDeck MCP server on %s:%s...", host, port)
    logger.info("Transport: SSE")
    
    # Import and run the MCP server
    from egile_mcp_slidedeck.server import mcp
    
    # Run with SSE transport
    sys.argv = ["server.py", "--transport", "sse", "--host", host, "--port", port]
    mcp.run()


if __name__ == "__main__":
    run_mcp_only()
