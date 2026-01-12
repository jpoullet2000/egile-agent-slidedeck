# Egile Agent Hub - SlideDeck Integration Guide

How to add the SlideDeck agent to egile-agent-hub for multi-agent workflows.

## Installation

The SlideDeck agent auto-registers with the hub when installed.

```bash
# In your hub environment
cd egile-agent-slidedeck
pip install -e .
```

## Configuration

Add to your `agents.yaml`:

```yaml
agents:
  - name: slidedeck
    description: "Creates professional PowerPoint presentations with AI"
    plugin_type: slidedeck
    mcp_port: 8003
    mcp_host: localhost
    instructions:
      - "You are a professional presentation designer"
      - "Always ask about target audience before starting"
      - "Keep slides focused and concise"
      - "Suggest images for key concepts"
    model_override:
      provider: xai
      model: grok-4-1-fast-reasoning
```

## Environment Variables

Add to hub's `.env`:

```bash
# LLM Keys (if not already present)
XAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here

# Image generation (optional)
REPLICATE_API_TOKEN=your_token_here
```

## Multi-Agent Teams

### Example 1: Sales Automation Team

```yaml
teams:
  - name: sales-team
    description: "Complete sales workflow automation"
    members:
      - prospectfinder
      - slidedeck
      - xtwitter
    instructions:
      - "Find prospects in target sector"
      - "Create tailored pitch deck for prospects"
      - "Announce deck on social media"
```

**Usage**:
```
User: Find 10 AI companies in Belgium and create a pitch deck

Hub orchestrates:
1. ProspectFinder: Searches for AI companies
2. SlideDeck: Creates deck with prospect data
3. XTwitter: Announces the deck
```

### Example 2: Content Marketing Team

```yaml
teams:
  - name: content-team
    description: "Content creation and distribution"
    members:
      - slidedeck
      - xtwitter
    instructions:
      - "Create engaging presentations"
      - "Promote content on social media"
```

**Usage**:
```
User: Create a webinar deck about AI trends and promote it

Hub orchestrates:
1. SlideDeck: Creates comprehensive deck
2. XTwitter: Creates promotional tweets
```

## Solo Agent Usage

Use SlideDeck independently:

```yaml
agents:
  - name: presentation-expert
    description: "Expert at creating professional presentations"
    plugin_type: slidedeck
    mcp_port: 8003
    instructions:
      - "You are a presentation design expert"
      - "Guide users through creating compelling decks"
      - "Optimize content for target audiences"
      - "Suggest visual elements and structure"
    model_override:
      provider: xai
      model: grok-4-1-fast-reasoning
    markdown: true
```

## Starting the Hub

```bash
cd egile-agent-hub
python -m egile_agent_hub.run_server
```

The hub will:
1. Discover the slidedeck plugin
2. Start MCP server on port 8003
3. Register the agent with AgentOS
4. Make it available in Agent UI

## Example Workflows

### Workflow 1: Research → Present

```yaml
teams:
  - name: research-presentation
    members:
      - prospectfinder
      - slidedeck
```

Request: "Research quantum computing companies and create a market analysis deck"

### Workflow 2: Create → Announce → Share

```yaml
teams:
  - name: content-distribution
    members:
      - slidedeck
      - xtwitter
```

Request: "Create a product launch deck and announce it on Twitter"

## Advanced Configuration

### Custom Audience Presets

```yaml
agents:
  - name: executive-presenter
    plugin_type: slidedeck
    mcp_port: 8003
    instructions:
      - "Always use 'ceo' audience by default"
      - "Focus on business impact and ROI"
      - "Keep slides high-level and strategic"
      - "Use temperature 0.7 for engaging content"
    model_override:
      provider: xai
      model: grok-4-1-fast-reasoning
```

### Technical Deep-Dive Preset

```yaml
agents:
  - name: technical-presenter
    plugin_type: slidedeck
    mcp_port: 8003
    instructions:
      - "Always use 'engineer' or 'cto' audience"
      - "Include technical details and architecture"
      - "Use temperature 0.3 for precision"
      - "Suggest architecture diagrams"
    model_override:
      provider: xai
      model: grok-4-1-fast-reasoning
```

## Verification

Check that slidedeck is discovered:

```bash
python -m egile_agent_hub.plugin_loader
```

Should show:
```
Available plugins:
  - prospectfinder
  - xtwitter
  - slidedeck  ← Your new plugin
```

## Troubleshooting

**Plugin not discovered**:
- Ensure egile-agent-slidedeck is installed
- Check package name is `egile-agent-slidedeck`
- Verify entry point in pyproject.toml

**MCP server conflicts**:
- Each agent needs unique `mcp_port`
- Default ports: prospectfinder=8001, xtwitter=8002, slidedeck=8003

**Model issues**:
- Verify API keys in hub's `.env`
- Check model_override provider is valid (xai, mistral, openai)

## Next Steps

- Create custom team configurations
- Integrate with your existing agents
- Build automated content workflows
- See [egile-agent-hub documentation](../egile-agent-hub/README.md)
