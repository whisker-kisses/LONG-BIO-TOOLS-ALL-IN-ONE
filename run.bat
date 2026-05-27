@echo off
REM Windows Batch Script to Run All Projects
REM Run all three projects asynchronously

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║     🚀 STARTING ALL PROJECTS (JWT + Bio API + Bot) 🚀     ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python is not installed or not in PATH
    echo   Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist ".env" (
    echo ⚠️  WARNING: .env file not found!
    echo    Creating .env file template...
    echo DISCORD_TOKEN=your_discord_bot_token_here > .env
    echo PORT=5005 >> .env
    echo.
    echo 📝 Please edit .env file and add your DISCORD_TOKEN
    echo.
)

REM Install/upgrade dependencies
echo 📦 Installing dependencies...
pip install -r requirements.txt --quiet

if errorlevel 1 (
    echo ❌ ERROR: Failed to install dependencies
    pause
    exit /b 1
)

REM Run the main script
echo.
echo ✅ All systems ready! Starting projects...
echo.

python main.py

if errorlevel 1 (
    echo ❌ ERROR: Failed to start projects
    pause
    exit /b 1
)

pause
