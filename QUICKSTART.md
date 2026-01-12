# Quick Start - Egile Agent SlideDeck

Get started with conversational slide deck creation in 5 minutes.

## 1. Install

```bash
# Install both packages
cd egile-agent-slidedeck
./install.bat  # Windows
# OR
./install.sh   # Linux/Mac
```

## 2. Configure

Edit `.env`:

```bash
# At least one LLM API key
XAI_API_KEY=your_key_here

# Content generation (optional)
ANTHROPIC_API_KEY=your_key_here
```

## 3. Start the System

```bash
slidedeck
```

This starts:
- MCP server on port 8003
- AgentOS on port 8000

## 4. Connect Agent UI

In a separate terminal:

```bash
cd ../agent-ui
pnpm dev
```

Open http://localhost:3000 and connect to http://localhost:8000

## 5. Create Your First Deck

In the Agent UI, chat with the agent:

```
You: Create a presentation about our AI platform for CTOs

Agent: I'd be happy to help! Let me create a technical presentation 
for CTOs. What's the main focus - architecture, scalability, security, 
or a mix?

You: Focus on architecture and scalability, about 8 slides

Agent: Perfect! Starting a new deck...

[Agent creates deck with slides]

Agent: I've created 8 slides covering:
1. Title: AI Platform Architecture
2. Platform Overview
3. Microservices Architecture
4. Scalability Strategy
... etc

Would you like me to add more slides or export the presentation?

You: Export as "platform_architecture.pptx"

Agent: ✅ Exported to ./presentations/platform_architecture_20260111_143022.pptx
```

## 6. Alternative: Programmatic Usage

```python
from egile_agent_core import Agent
from egile_agent_core.models import XAI
from egile_agent_slidedeck import SlideDeckPlugin

plugin = SlideDeckPlugin()
agent = Agent(
    name="slidedeck",
    model=XAI(model="grok-4-1-fast-reasoning"),
    plugins=[plugin]
)

response = await agent.process(
    "Create a 5-slide presentation about cloud security for CISOs"
)
```

## 7. Use with egile-agent-hub

Add to `agents.yaml`:

```yaml
agents:
  - name: slidedeck
    plugin_type: slidedeck
    mcp_port: 8003
    model_override:
      provider: xai
      model: grok-4-1-fast-reasoning
```

Then:

```bash
cd ../egile-agent-hub
python -m egile_agent_hub.run_server
```

## Best Practices

**Audience Selection**:
- Ask the agent to suggest the right audience
- CTOs get technical architecture details
- CEOs get business impact focus
- Engineers get implementation specifics

**Image Usage**:
- The agent suggests when images would help
- Be specific with image prompts
- Use 1-2 images per 5-10 slides

**Slide Count**:
- 5-7 slides for quick overview
- 10-15 slides for standard presentation
- 20+ slides for comprehensive deck

## Troubleshooting

**Agent not responding**:
- Check MCP server is running (port 8003)
- Check AgentOS is running (port 8000)
- Verify API keys in `.env`

**Images not generating**:
- Add `REPLICATE_API_TOKEN` or `STABILITY_API_KEY`
- Images are optional - content will still work

**Export fails**:
- Check `OUTPUT_DIR` exists and is writable
- Verify at least one slide was added

## Next Steps

- See [README.md](README.md) for full documentation
- Try multi-agent workflows with egile-agent-hub
- Customize agent instructions in `agents.yaml`
