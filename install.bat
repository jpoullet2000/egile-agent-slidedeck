@echo off
REM Installation script for egile-agent-slidedeck (Windows)

echo ============================================================
echo Installing Egile Agent SlideDeck
echo ============================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10 or higher
    pause
    exit /b 1
)

echo Step 1: Installing egile-mcp-slidedeck...
cd ..\egile-mcp-slidedeck
pip install -e .
if errorlevel 1 (
    echo ERROR: Failed to install egile-mcp-slidedeck
    pause
    exit /b 1
)

echo.
echo Step 2: Installing egile-agent-slidedeck...
cd ..\egile-agent-slidedeck
pip install -e .
if errorlevel 1 (
    echo ERROR: Failed to install egile-agent-slidedeck
    pause
    exit /b 1
)

echo.
echo Step 3: Copying environment template...
if not exist .env (
    copy .env.example .env
    echo Created .env file - please configure your API keys
) else (
    echo .env file already exists - skipping
)

echo.
echo ============================================================
echo Installation Complete!
echo ============================================================
echo.
echo NEXT STEPS:
echo 1. Edit .env and add your API keys
echo 2. Run: slidedeck
echo 3. Connect Agent UI to http://localhost:8000
echo.
echo Or run components separately:
echo   - slidedeck-mcp    (MCP server only)
echo   - slidedeck-agent  (AgentOS only)
echo.
pause
