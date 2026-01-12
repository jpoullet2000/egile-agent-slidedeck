"""Run only the AgentOS (without MCP server)."""

from __future__ import annotations

import logging
import os

import uvicorn
from dotenv import load_dotenv

from egile_agent_core.models import OpenAI, XAI, Mistral
from egile_agent_core.server import create_agent_os

from .plugin import SlideDeckPlugin

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

load_dotenv()


def run_agent_only():
    """Run only the AgentOS (MCP server must be started separately)."""
    logger.info("Starting SlideDeck AgentOS (MCP mode)...")
    logger.info("Make sure the MCP server is running on port %s", os.getenv("MCP_PORT", "8003"))
    
    plugin = SlideDeckPlugin(
        mcp_host=os.getenv("MCP_HOST", "localhost"),
        mcp_port=int(os.getenv("MCP_PORT", "8003")),
        mcp_transport=os.getenv("MCP_TRANSPORT", "sse"),
        use_mcp=True,
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

    uvicorn.run(
        agent_os.app,
        host=os.getenv("AGENTOS_HOST", "0.0.0.0"),
        port=int(os.getenv("AGENTOS_PORT", "8000")),
        log_level="info",
    )


if __name__ == "__main__":
    run_agent_only()
