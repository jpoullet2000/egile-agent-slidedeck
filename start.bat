@echo off
REM Start script for egile-agent-slidedeck (Windows)

echo ============================================================
echo Starting Egile Agent SlideDeck
echo ============================================================
echo.

REM Check if installed
python -c "import egile_agent_slidedeck" >nul 2>&1
if errorlevel 1 (
    echo ERROR: egile-agent-slidedeck is not installed
    echo Please run install.bat first
    pause
    exit /b 1
)

echo Starting SlideDeck system...
echo.
echo MCP Server: http://localhost:8003
echo AgentOS:    http://localhost:8000
echo.
echo Press Ctrl+C to stop
echo.

python -m egile_agent_slidedeck.run_server
