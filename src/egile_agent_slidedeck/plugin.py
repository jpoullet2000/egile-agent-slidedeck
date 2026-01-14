"""SlideDeck plugin for Egile Agent Core."""

from __future__ import annotations

import logging
import re
from typing import TYPE_CHECKING, Any, Optional

from egile_agent_core.plugins import Plugin

if TYPE_CHECKING:
    from egile_agent_core.agent import Agent

logger = logging.getLogger(__name__)


class SlideDeckPlugin(Plugin):
    """
    Plugin that provides slide deck generation capabilities.
    
    This plugin integrates with the egile-mcp-slidedeck MCP server to enable
    AI agents to create professional PowerPoint presentations with AI-generated
    content and images.
    """

    def __init__(
        self,
        mcp_host: str = "localhost",
        mcp_port: int = 8003,
        mcp_transport: str = "sse",
        mcp_command: Optional[str] = None,
        timeout: float = 60.0,
        use_mcp: bool = True,
    ):
        """
        Initialize the SlideDeck plugin.

        Args:
            mcp_host: Host where the MCP server is running
            mcp_port: Port where the MCP server is running
            mcp_transport: Transport mode - "stdio" or "sse"
            mcp_command: Command to start MCP server (for stdio transport)
            timeout: Request timeout in seconds (longer for image generation)
            use_mcp: If True, use MCP client; if False, use direct service
        """
        self.mcp_host = mcp_host
        self.mcp_port = mcp_port
        self.mcp_transport = mcp_transport
        self.mcp_command = mcp_command or "python -m egile_mcp_slidedeck.server"
        self.timeout = timeout
        self.use_mcp = use_mcp
        self._client: Optional[Any] = None
        self._deck_service = None
        self._agent: Optional[Agent] = None
        self._current_deck_id: Optional[str] = None

    @property
    def name(self) -> str:
        """Plugin name for registration."""
        return "slidedeck"

    @property
    def description(self) -> str:
        """Plugin description."""
        return (
            "Creates professional PowerPoint presentations with AI-generated content and images. "
            "Supports multiple audiences (CEO, CTO, Engineer) and various slide types."
        )

    @property
    def version(self) -> str:
        """Plugin version."""
        return "0.1.0"

    @property
    def mcp_server_module(self) -> str:
        """MCP server module path."""
        return "egile_mcp_slidedeck.server"

    async def on_agent_start(self, agent: Agent) -> None:
        """Called when the agent starts."""
        self._agent = agent
        
        if self.use_mcp:
            # Use MCP client
            try:
                from .mcp_client import MCPClient
                self._client = MCPClient(
                    transport=self.mcp_transport,
                    host=self.mcp_host,
                    port=self.mcp_port,
                    command=self.mcp_command,
                    timeout=self.timeout,
                )
                await self._client.connect()
                logger.info(f"SlideDeck plugin connected to MCP server via {self.mcp_transport}")
            except Exception as e:
                logger.error(f"Failed to connect to MCP server: {e}")
                raise
        else:
            # Use direct mode
            from egile_mcp_slidedeck.deck_service import DeckService
            self._deck_service = DeckService()
            logger.info("SlideDeck plugin initialized in direct mode")

    async def start_deck(
        self,
        title: str,
        audience: str = "general",
        template: str = "corporate"
    ) -> str:
        """
        Start a new presentation deck.
        
        Args:
            title: Deck title
            audience: Target audience (ceo, cto, engineer, general)
            template: Template name (corporate, minimal, creative)
            
        Returns:
            Formatted response with deck ID
        """
        if not title:
            return "Error: Deck title is required"
        
        logger.info(f"Starting deck: {title}, audience: {audience}")
        
        try:
            if self.use_mcp and self._client:
                result = await self._client.call_tool("start_deck", {
                    "title": title,
                    "audience": audience,
                    "template": template
                })
            else:
                response = self._deck_service.start_new_deck(title, audience, template)
                result = self._format_deck_start_response(response)
            
            # Extract and cache deck ID
            self._extract_and_cache_deck_id(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error starting deck: {e}")
            return f"Error starting deck: {str(e)}"

    async def add_slide(
        self,
        content: str,
        slide_type: str = "content",
        deck_id: str = "",
        audience: str = "",
        include_image: bool = False,
        image_prompt: str = "",
        temperature: float = 0.7
    ) -> str:
        """
        Add a slide to the current deck.
        
        Args:
            content: Slide content or topic
            slide_type: Type of slide (title, content, image, summary)
            deck_id: Target deck ID (optional, uses current deck if not provided)
            audience: Override audience for this slide
            include_image: Whether to include an image
            image_prompt: Prompt for image generation or URL
            temperature: LLM creativity (0.3-0.7)
            
        Returns:
            Formatted response with slide content
        """
        effective_deck_id = deck_id or self._current_deck_id
        
        if not effective_deck_id:
            return "Error: No active deck. Start a deck first with start_deck()."
        
        if not content:
            return "Error: Slide content is required"
        
        logger.info(f"Adding slide to deck {effective_deck_id}")
        
        try:
            if self.use_mcp and self._client:
                result = await self._client.call_tool("add_slide", {
                    "deck_id": effective_deck_id,
                    "content": content,
                    "slide_type": slide_type,
                    "audience": audience,
                    "include_image": include_image,
                    "image_prompt": image_prompt,
                    "temperature": temperature
                })
            else:
                response = self._deck_service.add_slide_to_deck(
                    deck_id=effective_deck_id,
                    content=content,
                    slide_type=slide_type,
                    audience=audience if audience else None,
                    include_image=include_image,
                    image_prompt=image_prompt if image_prompt else None,
                    temperature=temperature
                )
                result = self._format_slide_response(response)
            
            return result
            
        except Exception as e:
            logger.error(f"Error adding slide: {e}")
            return f"Error adding slide: {str(e)}"

    async def export_deck(
        self,
        deck_id: str = "",
        filename: str = ""
    ) -> str:
        """
        Export deck to PowerPoint format.
        
        Args:
            deck_id: Deck to export (optional, uses current deck)
            filename: Output filename (optional)
            
        Returns:
            Formatted response with export results
        """
        effective_deck_id = deck_id or self._current_deck_id
        
        if not effective_deck_id:
            return "Error: No active deck to export."
        
        logger.info(f"Exporting deck {effective_deck_id}")
        
        try:
            if self.use_mcp and self._client:
                result = await self._client.call_tool("export_deck", {
                    "deck_id": effective_deck_id,
                    "filename": filename
                })
            else:
                response = self._deck_service.export_deck(
                    deck_id=effective_deck_id,
                    filename=filename if filename else None
                )
                result = self._format_export_response(response)
            
            return result
            
        except Exception as e:
            logger.error(f"Error exporting deck: {e}")
            return f"Error exporting deck: {str(e)}"

    async def get_deck_info(self, deck_id: str = "") -> str:
        """Get information about a deck."""
        effective_deck_id = deck_id or self._current_deck_id
        
        if not effective_deck_id:
            return "Error: No deck ID provided."
        
        try:
            if self.use_mcp and self._client:
                result = await self._client.call_tool("get_deck_info", {
                    "deck_id": effective_deck_id
                })
            else:
                response = self._deck_service.get_deck_info(effective_deck_id)
                result = self._format_info_response(response)
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting deck info: {e}")
            return f"Error: {str(e)}"

    async def list_decks(self) -> str:
        """List all active decks."""
        try:
            if self.use_mcp and self._client:
                result = await self._client.call_tool("list_decks", {})
            else:
                response = self._deck_service.list_decks()
                result = self._format_list_response(response)
            
            return result
            
        except Exception as e:
            logger.error(f"Error listing decks: {e}")
            return f"Error: {str(e)}"

    async def cleanup(self) -> None:
        """Clean up resources when agent stops."""
        if self._client:
            await self._client.close()
            self._client = None

    def _extract_and_cache_deck_id(self, response: str) -> None:
        """Extract deck ID from response and cache it."""
        match = re.search(r"Deck ID:\s*([a-f0-9\-]+)", response, re.IGNORECASE)
        if match:
            self._current_deck_id = match.group(1)
            logger.info(f"Cached deck ID: {self._current_deck_id}")

    def _format_deck_start_response(self, response: dict) -> str:
        """Format deck start response for non-MCP mode."""
        if not response["success"]:
            return f"❌ Error: {response['error']}"
        
        output = f"✅ New Deck Started Successfully!\n\n"
        output += f"📊 DECK INFORMATION:\n{'-' * 60}\n"
        output += f"Deck ID: {response['deck_id']}\n"
        output += f"Title: {response['title']}\n"
        output += f"Audience: {response['audience']}\n"
        output += f"Template: {response['template']}\n"
        output += f"{'-' * 60}\n\n"
        output += f"💡 NEXT STEPS:\n"
        output += f"  - Use add_slide() to add slides\n"
        output += f"  - Use export_deck() when ready\n"
        
        return output

    def _format_slide_response(self, response: dict) -> str:
        """Format slide addition response for non-MCP mode."""
        if not response["success"]:
            return f"❌ Error: {response['error']}"
        
        output = f"✅ Slide Added Successfully!\n\n"
        output += f"📄 SLIDE CONTENT:\n{'-' * 60}\n"
        output += f"Title: {response['title']}\n\n"
        output += f"Content:\n{response['content']}\n"
        output += f"{'-' * 60}\n\n"
        output += f"📊 METADATA:\n"
        output += f"  • Slide Number: {response['slide_number']}\n"
        output += f"  • Type: {response['type']}\n"
        output += f"  • Audience: {response['audience']}\n"
        output += f"  • Has Image: {response['has_image']}\n"
        
        return output

    def _format_export_response(self, response: dict) -> str:
        """Format export response for non-MCP mode."""
        if not response["success"]:
            return f"❌ Error: {response['error']}"
        
        output = f"✅ POWERPOINT FILE CREATED SUCCESSFULLY!\n\n"
        output += f"📁 FILE LOCATION:\n{'-' * 60}\n"
        output += f"📄 {response['output_path']}\n"
        output += f"{'-' * 60}\n\n"
        output += f"📊 FILE DETAILS:\n"
        output += f"  • Slide Count: {response['slide_count']} slides\n"
        
        if not response.get("dry_run") and response.get("file_size"):
            file_size_kb = response['file_size'] / 1024
            file_size_mb = response['file_size'] / (1024 * 1024)
            if file_size_mb >= 1:
                output += f"  • File Size: {file_size_mb:.2f} MB\n"
            else:
                output += f"  • File Size: {file_size_kb:.2f} KB\n"
        
        output += f"\n🎉 Your PowerPoint presentation has been saved!\n"
        output += f"   You can now open the .pptx file in PowerPoint, Google Slides,\n"
        output += f"   or any compatible presentation software.\n"
        
        return output

    def _format_info_response(self, response: dict) -> str:
        """Format deck info response."""
        if not response["success"]:
            return f"❌ Error: {response['error']}"
        
        output = f"📊 DECK INFORMATION:\n{'-' * 60}\n"
        output += f"Deck ID: {response['deck_id']}\n"
        output += f"Title: {response['title']}\n"
        output += f"Slide Count: {response['slide_count']}\n"
        output += f"{'-' * 60}\n"
        
        return output

    def _format_list_response(self, response: dict) -> str:
        """Format deck list response."""
        if response['count'] == 0:
            return "No decks found."
        
        output = f"📚 ACTIVE DECKS ({response['count']}):\n{'-' * 60}\n"
        for deck in response['decks']:
            output += f"\n{deck['title']}\n"
            output += f"  ID: {deck['deck_id']}\n"
            output += f"  Slides: {deck['slide_count']}\n"
        
        return output

    def get_tool_functions(self) -> dict[str, Any]:
        """
        Get the tool functions that can be called by the agent.
        
        Returns:
            Dictionary mapping function names to their implementations
        """
        return {
            "start_deck": self.start_deck,
            "add_slide": self.add_slide,
            "export_deck": self.export_deck,
            "get_deck_info": self.get_deck_info,
            "list_decks": self.list_decks,
        }

    def get_default_instructions(self) -> list[str]:
        """Get default instructions for the agent."""
        return [
            "You are a professional presentation designer and content strategist.",
            "You help users create compelling PowerPoint presentations.",
            "",
            "WORKFLOW:",
            "1. Start every presentation with start_deck(title, audience)",
            "2. Add slides one at a time with add_slide(content, ...)",
            "3. Export when ready with export_deck()",
            "",
            "BEST PRACTICES:",
            "- Ask the user about their target audience (CEO, CTO, Engineer, or General)",
            "- Suggest appropriate slide types for different content",
            "- Keep slides focused with 3-5 bullet points maximum",
            "- Offer to include relevant images on key slides",
            "- Preview the deck structure before exporting",
            "",
            "IMAGE GUIDELINES:",
            "- Use images sparingly (1-2 per 5-10 slides)",
            "- Generate images for concept visualization, not decoration",
            "- Use specific prompts like 'modern data dashboard' not 'nice picture'",
            "",
            "TEMPERATURE GUIDE:",
            "- 0.3: Technical, precise (good for engineer/CTO slides with data)",
            "- 0.7: Creative, engaging (good for CEO/general slides)",
            "",
            "NEVER:",
            "- Create slides without starting a deck first",
            "- Export without confirming the user is ready",
            "- Add more than 15-20 slides without checking with the user"
        ]
