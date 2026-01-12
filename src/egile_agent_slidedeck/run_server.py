"""Run MCP server + AgentOS for the SlideDeck agent."""

from __future__ import annotations

import asyncio
import logging
import os
import subprocess
import sys
from pathlib import Path

import uvicorn
from dotenv import load_dotenv

from egile_agent_core.models import OpenAI, XAI, Mistral
from egile_agent_core.server import create_agent_os

from .plugin import SlideDeckPlugin

log_level = os.getenv("FASTMCP_LOG_LEVEL", os.getenv("LOG_LEVEL", "INFO")).upper()
log_file = os.getenv("LOG_FILE")

logging.basicConfig(
    level=getattr(logging, log_level, logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename=log_file if log_file else None,
)
logger = logging.getLogger(__name__)

load_dotenv()


def create_slidedeck_agent_os():
    """Create AgentOS with SlideDeck plugin."""
    plugin = SlideDeckPlugin(
        mcp_host=os.getenv("MCP_HOST", "localhost"),
        mcp_port=int(os.getenv("MCP_PORT", "8003")),
        mcp_transport=os.getenv("MCP_TRANSPORT", "sse"),
    )

    # Model selection priority: XAI > Mistral > OpenAI
    if os.getenv("XAI_API_KEY"):
        model = XAI(model=os.getenv("XAI_MODEL", "grok-4-1-fast-reasoning"))
    elif os.getenv("MISTRAL_API_KEY"):
        model = Mistral(model=os.getenv("MISTRAL_MODEL", "mistral-large-2512"))
    else:
        model = OpenAI(model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"))

    agents_config = [
        {
            "name": "slidedeck",
            "model": model,
            "description": "AI agent that creates professional PowerPoint presentations.",
            "instructions": plugin.get_default_instructions(),
            "plugins": [plugin],
            "markdown": True,
        }
    ]

    agent_os = create_agent_os(
        agents_config=agents_config,
        os_id="slidedeck-os",
        description="SlideDeck AgentOS - Create professional presentations with AI",
    )
    return agent_os


async def start_mcp_server():
    """Start the MCP server in a subprocess."""
    port = os.getenv("MCP_PORT", "8003")
    host = os.getenv("MCP_HOST", "0.0.0.0")
    logger.info("Starting MCP server on %s:%s...", host, port)
    mcp_module = "egile_mcp_slidedeck.server"

    env = os.environ.copy()
    env.setdefault("PYTHONIOENCODING", "utf-8")

    process = subprocess.Popen(
        [sys.executable, "-m", mcp_module, "--transport", "sse", "--host", host, "--port", port],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
    )

    await asyncio.sleep(2)

    if process.poll() is not None:
        stderr = process.stderr.read() if process.stderr else ""
        logger.error("MCP server failed to start: %s", stderr)
        return None

    logger.info("MCP server started successfully on %s:%s", host, port)
    return process


def start_agent_ui_instructions():
    """Log instructions to start the Agent UI."""
    ui_path = Path(__file__).parent.parent.parent.parent / "agent-ui"
    logger.info("\n" + "=" * 60)
    logger.info("To start the Agent UI, run in a separate terminal:")
    logger.info("=" * 60)
    if ui_path.exists():
        logger.info("cd %s", ui_path)
        logger.info("pnpm dev")
    else:
        logger.info("cd /path/to/agent-ui")
        logger.info("pnpm dev")
    logger.info("\nThen open: http://localhost:3000")
    logger.info(f"Connect to: http://localhost:{os.getenv('AGENTOS_PORT', '8000')}")
    logger.info("=" * 60 + "\n")


async def run_all_async():
    """Run both MCP server and AgentOS."""
    logger.info("Starting SlideDeck system...")
    
    # Start MCP server
    mcp_process = await start_mcp_server()
    
    if not mcp_process:
        logger.error("Failed to start MCP server. Exiting.")
        return
    
    # Create AgentOS
    logger.info("Creating AgentOS...")
    agent_os = create_slidedeck_agent_os()
    
    # Log Agent UI instructions
    start_agent_ui_instructions()
    
    # Run AgentOS
    try:
        logger.info("Starting AgentOS on port %s...", os.getenv("AGENTOS_PORT", "8000"))
        config = uvicorn.Config(
            agent_os.app,
            host=os.getenv("AGENTOS_HOST", "0.0.0.0"),
            port=int(os.getenv("AGENTOS_PORT", "8000")),
            log_level="info",
        )
        server = uvicorn.Server(config)
        await server.serve()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        if mcp_process:
            mcp_process.terminate()
            mcp_process.wait()
            logger.info("MCP server stopped")


def run_all():
    """Entry point for running the complete system."""
    asyncio.run(run_all_async())


if __name__ == "__main__":
    run_all()
