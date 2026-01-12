"""Egile Agent SlideDeck - Conversational presentation generation agent."""

__version__ = "0.1.0"

from egile_agent_slidedeck.plugin import SlideDeckPlugin
from egile_agent_slidedeck.run_server import run_all

__all__ = ["SlideDeckPlugin", "run_all"]
