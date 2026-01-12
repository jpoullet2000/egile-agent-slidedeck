#!/bin/bash
# Installation script for egile-agent-slidedeck (Linux/Mac)

echo "============================================================"
echo "Installing Egile Agent SlideDeck"
echo "============================================================"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.10 or higher"
    exit 1
fi

echo "Step 1: Installing egile-mcp-slidedeck..."
cd ../egile-mcp-slidedeck || exit 1
pip install -e . || {
    echo "ERROR: Failed to install egile-mcp-slidedeck"
    exit 1
}

echo ""
echo "Step 2: Installing egile-agent-slidedeck..."
cd ../egile-agent-slidedeck || exit 1
pip install -e . || {
    echo "ERROR: Failed to install egile-agent-slidedeck"
    exit 1
}

echo ""
echo "Step 3: Copying environment template..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env file - please configure your API keys"
else
    echo ".env file already exists - skipping"
fi

echo ""
echo "============================================================"
echo "Installation Complete!"
echo "============================================================"
echo ""
echo "NEXT STEPS:"
echo "1. Edit .env and add your API keys"
echo "2. Run: slidedeck"
echo "3. Connect Agent UI to http://localhost:8000"
echo ""
echo "Or run components separately:"
echo "  - slidedeck-mcp    (MCP server only)"
echo "  - slidedeck-agent  (AgentOS only)"
echo ""
