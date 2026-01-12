#!/bin/bash
# Start script for egile-agent-slidedeck (Linux/Mac)

echo "============================================================"
echo "Starting Egile Agent SlideDeck"
echo "============================================================"
echo ""

# Check if installed
python3 -c "import egile_agent_slidedeck" 2>/dev/null || {
    echo "ERROR: egile-agent-slidedeck is not installed"
    echo "Please run install.sh first"
    exit 1
}

echo "Starting SlideDeck system..."
echo ""
echo "MCP Server: http://localhost:8003"
echo "AgentOS:    http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop"
echo ""

python3 -m egile_agent_slidedeck.run_server
