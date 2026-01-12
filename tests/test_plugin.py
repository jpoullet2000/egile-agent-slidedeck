"""Tests for SlideDeck plugin."""

import pytest
from egile_agent_slidedeck.plugin import SlideDeckPlugin


def test_plugin_creation():
    """Test plugin can be created."""
    plugin = SlideDeckPlugin(use_mcp=False)
    assert plugin is not None
    assert plugin.name == "slidedeck"


def test_plugin_properties():
    """Test plugin properties."""
    plugin = SlideDeckPlugin()
    
    assert plugin.name == "slidedeck"
    assert plugin.version == "0.1.0"
    assert "PowerPoint" in plugin.description


def test_plugin_instructions():
    """Test plugin provides default instructions."""
    plugin = SlideDeckPlugin()
    instructions = plugin.get_default_instructions()
    
    assert isinstance(instructions, list)
    assert len(instructions) > 0
    assert any("start_deck" in str(inst) for inst in instructions)


@pytest.mark.asyncio
async def test_plugin_direct_mode():
    """Test plugin in direct mode (no MCP)."""
    plugin = SlideDeckPlugin(use_mcp=False)
    
    # Mock agent
    class MockAgent:
        pass
    
    await plugin.on_agent_start(MockAgent())
    
    # Should have deck service
    assert plugin._deck_service is not None
