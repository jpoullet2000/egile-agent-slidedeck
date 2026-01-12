# Egile Agent SlideDeck

Conversational AI agent for creating professional PowerPoint presentations through natural language interaction.

## Features

- **Natural Language Interface**: Create presentations through conversation
- **AI-Powered**: Uses XAI (Grok), Mistral, or OpenAI for intelligent agent responses
- **MCP Integration**: Connects to egile-mcp-slidedeck for slide generation
- **AgentOS Compatible**: Works with Agent UI for web-based interaction
- **Hub Integration**: Auto-discovered by egile-agent-hub for multi-agent workflows
- **Audience-Aware**: Automatically optimizes content for different audiences
- **Guided Workflow**: Helps users through the presentation creation process

## Installation

### Quick Install

```bash
# Install both agent and MCP server
pip install -e .
pip install -e ../egile-mcp-slidedeck
```

### With egile-agent-core

```bash
# If egile-agent-core is not installed
pip install egile-agent-core
```

## Configuration

Create a `.env` file:

```bash
# LLM API Keys (at least one required)
XAI_API_KEY=your_xai_key_here
MISTRAL_API_KEY=your_mistral_key_here
OPENAI_API_KEY=your_openai_key_here

# For content generation (inherited from MCP server)
ANTHROPIC_API_KEY=your_anthropic_key_here

# MCP Server
MCP_HOST=localhost
MCP_PORT=8003
MCP_TRANSPORT=sse

# AgentOS
AGENTOS_HOST=0.0.0.0
AGENTOS_PORT=8000

# Output
OUTPUT_DIR=./presentations
```

## Usage

### Run Complete System (MCP + AgentOS)

```bash
# All-in-one: Starts MCP server and AgentOS
slidedeck

# Or via Python
python -m egile_agent_slidedeck.run_server
```

Then:
1. MCP server runs on port 8003
2. AgentOS runs on port 8000
3. Connect Agent UI to http://localhost:8000

### Run Components Separately

```bash
# Terminal 1: MCP server only
slidedeck-mcp

# Terminal 2: AgentOS only
slidedeck-agent
```

### As Plugin in egile-agent-hub

The agent auto-registers with egile-agent-hub. Add to `agents.yaml`:

```yaml
agents:
  - name: slidedeck
    description: "Creates professional PowerPoint presentations"
    plugin_type: slidedeck
    mcp_port: 8003
    instructions:
      - "Help users create compelling presentations"
      - "Ask about target audience before starting"
    model_override:
      provider: xai
      model: grok-4-1-fast-reasoning
```

### Programmatic Usage

```python
from egile_agent_core import Agent
from egile_agent_core.models import XAI
from egile_agent_slidedeck import SlideDeckPlugin

# Create plugin
plugin = SlideDeckPlugin(
    mcp_host="localhost",
    mcp_port=8003,
    use_mcp=True
)

# Create agent
agent = Agent(
    name="slidedeck",
    model=XAI(model="grok-4-1-fast-reasoning"),
    plugins=[plugin],
    system_prompt="You are a presentation design expert."
)

# Use the agent
response = await agent.process(
    "Create a presentation about our AI platform for CTOs"
)
```

## Conversational Workflow

The agent guides users through:

1. **Discovery**: Asks about audience, topic, and goals
2. **Structure**: Suggests slide outline
3. **Creation**: Generates slides one by one
4. **Refinement**: Allows editing and additions
5. **Export**: Produces final PowerPoint file

### Example Conversation

```
User: I need a presentation about our AI platform

Agent: I'd be happy to help! A few questions:
- Who is your target audience? (CEO, CTO, Engineers, or General)
- What's the main message you want to convey?
- How many slides are you thinking?

User: CTOs, about 10 slides, focus on architecture and scalability

Agent: Perfect! I'll create a technical presentation for CTOs. 
Let me start with a title slide...

[Agent starts deck and creates slides]

Agent: I've created your presentation with 10 slides covering:
- Title: AI Platform Architecture
- Platform Overview
- System Architecture
- Scalability Strategy
- [etc.]

Would you like to export it now, or make any changes?

User: Export it as "platform_architecture.pptx"

Agent: Exported successfully to ./presentations/platform_architecture.pptx!
```

## Available Functions

When using the plugin, the agent has access to:

- `start_deck(title, audience, template)`: Start new presentation
- `add_slide(content, slide_type, ...)`: Add slide with AI content
- `export_deck(deck_id, filename)`: Export to PowerPoint
- `get_deck_info(deck_id)`: Get deck information
- `list_decks()`: List all active decks

## Agent Instructions

The agent follows these best practices:

**Workflow**:
1. Always start with `start_deck()`
2. Add slides one at a time
3. Export when user is ready

**Content**:
- Ask about target audience
- Keep slides focused (3-5 bullets)
- Suggest appropriate slide types
- Offer images for key concepts

**Images**:
- Use sparingly (1-2 per 5-10 slides)
- Generate for concepts, not decoration
- Use specific prompts

**Temperature**:
- 0.3 for technical/data slides
- 0.7 for creative/engaging slides

## Integration with egile-agent-hub

Auto-discovered when installed:

```bash
# Install in hub environment
pip install -e /path/to/egile-agent-slidedeck
```

The hub automatically:
- Detects the plugin via package name
- Loads SlideDeckPlugin class
- Starts MCP server on configured port
- Registers agent with AgentOS

## Multi-Agent Workflows

Combine with other agents:

```yaml
teams:
  - name: sales-automation
    description: "Complete sales workflow automation"
    members:
      - prospectfinder    # Find prospects
      - slidedeck         # Create pitch deck
      - xtwitter          # Announce on social media
    instructions:
      - "Find prospects in target sector"
      - "Create tailored pitch deck"
      - "Craft social media announcement"
```

Example workflow:
```
User: Find 10 AI companies in Belgium and create a pitch deck

Hub: 
1. ProspectFinder searches for companies
2. SlideDeck creates deck with prospect data
3. XTwitter announces deck launch
```

## Console Scripts

After installation, these commands are available:

- `slidedeck`: Run complete system (MCP + AgentOS)
- `slidedeck-mcp`: Run MCP server only
- `slidedeck-agent`: Run AgentOS only

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `XAI_API_KEY` | One of three | - | xAI API key (preferred) |
| `MISTRAL_API_KEY` | One of three | - | Mistral API key |
| `OPENAI_API_KEY` | One of three | - | OpenAI API key |
| `MCP_HOST` | No | localhost | MCP server host |
| `MCP_PORT` | No | 8003 | MCP server port |
| `MCP_TRANSPORT` | No | sse | MCP transport (sse/stdio) |
| `AGENTOS_HOST` | No | 0.0.0.0 | AgentOS host |
| `AGENTOS_PORT` | No | 8000 | AgentOS port |
| `DB_FILE` | No | slidedeck_agent.db | Session database |

## Agent UI Integration

Connect the Agent UI:

1. Start the agent: `slidedeck`
2. Configure Agent UI `.env`:
   ```bash
   NEXT_PUBLIC_AGENTOS_URL=http://localhost:8000
   ```
3. Run Agent UI: `pnpm dev`
4. Open http://localhost:3000

The agent appears in the agent selector and supports:
- Streaming responses
- Markdown formatting
- Session persistence
- Multi-turn conversations

## Architecture

```
User (via Agent UI or CLI)
  ↓
AgentOS (port 8000)
  ↓
SlideDeck Agent (XAI/Mistral/OpenAI)
  ↓
SlideDeckPlugin
  ↓
MCP Client (SSE)
  ↓
egile-mcp-slidedeck (port 8003)
  ↓
[Content Generator, Image Handler, PPTX Generator]
  ↓
PowerPoint File (.pptx)
```

## Development

```bash
# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black .
ruff check .
```

## License

MIT

## Related Projects

- **egile-mcp-slidedeck**: MCP server for slide generation
- **egile-agent-core**: Core agent framework
- **egile-agent-hub**: Multi-agent orchestration
- **agent-ui**: Web interface for agents
