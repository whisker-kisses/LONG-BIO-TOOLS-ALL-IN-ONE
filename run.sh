#!/bin/bash
# Unix/Linux/macOS Shell Script to Run All Projects
# Run all three projects asynchronously

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║     🚀 STARTING ALL PROJECTS (JWT + Bio API + Bot) 🚀     ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ ERROR: Python 3 is not installed"
    echo "   Please install Python 3.8+ from https://www.python.org/"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  WARNING: .env file not found!"
    echo "   Creating .env file template..."
    cat > .env << EOF
DISCORD_TOKEN=your_discord_bot_token_here
PORT=5005
DEBUG=False
EOF
    echo ""
    echo "📝 Please edit .env file and add your DISCORD_TOKEN"
    echo ""
fi

# Install/upgrade dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt -q

if [ $? -ne 0 ]; then
    echo "❌ ERROR: Failed to install dependencies"
    exit 1
fi

# Run the main script
echo ""
echo "✅ All systems ready! Starting projects..."
echo ""

python3 main.py

exit $?
