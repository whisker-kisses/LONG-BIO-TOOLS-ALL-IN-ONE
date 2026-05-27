#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════
    Main Entry Point - Run All 3 Projects Asynchronously
    @watashii_ff
═══════════════════════════════════════════════════════════════
    1. JWT Token Generator API (Port 30326)
    2. Long Bio API (Port 5000)
    3. Discord Bot (Port 5005)
"""

import asyncio
import threading
import sys
import os
import time
import importlib.util
from pathlib import Path
from colorama import init, Fore, Style

# Initialize colorama for colored output
init(autoreset=True)

# ═══════════════════════════════════════════════════════════════
# Load Projects with Error Handling (Using importlib to avoid sys.path conflicts)
# ═══════════════════════════════════════════════════════════════

print(f"{Fore.CYAN}[STARTUP] Loading project modules...{Style.RESET_ALL}\n")

BASE_DIR = Path(__file__).parent
jwt_app = None
bio_api_app = None
discord_bot = None

def load_module_from_path(module_name, file_path, add_to_path=None):
    """Load a module from a specific file path"""
    try:
        # Temporarily add the directory to sys.path if needed
        temp_path = None
        if add_to_path:
            temp_path = str(add_to_path)
            sys.path.insert(0, temp_path)
        
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        
        # Clean up sys.path
        if temp_path and temp_path in sys.path:
            sys.path.remove(temp_path)
        
        return module
    except Exception as e:
        if temp_path and temp_path in sys.path:
            sys.path.remove(temp_path)
        raise e

# Load JWT Token Generator API
try:
    jwt_dir = BASE_DIR / "Acc-to-Jwt-Gen-Api-main"
    jwt_module = load_module_from_path("jwt_main", jwt_dir / "main.py", jwt_dir)
    jwt_app = jwt_module.app
    print(f"{Fore.GREEN}[OK] JWT Token Generator API loaded{Style.RESET_ALL}")
except Exception as e:
    print(f"{Fore.RED}[ERROR] Failed to load JWT API: {e}{Style.RESET_ALL}", flush=True)
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Load Long Bio API
try:
    bio_dir = BASE_DIR / "Long-bio-api-main"
    bio_module = load_module_from_path("bio_main", bio_dir / "app.py", bio_dir)
    bio_api_app = bio_module.app
    print(f"{Fore.GREEN}[OK] Long Bio API loaded{Style.RESET_ALL}")
except Exception as e:
    print(f"{Fore.RED}[ERROR] Failed to load Bio API: {e}{Style.RESET_ALL}", flush=True)
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Load Discord Bot
try:
    bot_dir = BASE_DIR / "Long-bio-bot-main"
    bot_module = load_module_from_path("bot_main", bot_dir / "app.py", bot_dir)
    discord_bot = bot_module.bot
    print(f"{Fore.GREEN}[OK] Discord Bot loaded{Style.RESET_ALL}\n")
except Exception as e:
    print(f"{Fore.RED}[ERROR] Failed to load Discord Bot: {e}{Style.RESET_ALL}", flush=True)
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ═══════════════════════════════════════════════════════════════
# Project Configurations
# ═══════════════════════════════════════════════════════════════

PROJECTS = {
    "JWT_API": {
        "name": "JWT Token Generator API",
        "port": 30326,
        "host": "0.0.0.0",
        "type": "flask"
    },
    "BIO_API": {
        "name": "Long Bio API",
        "port": 5000,
        "host": "0.0.0.0",
        "type": "flask"
    },
    "DISCORD_BOT": {
        "name": "Discord Bot",
        "port": 5005,
        "type": "discord"
    }
}

# ═══════════════════════════════════════════════════════════════
# Flask App Runner (In Separate Thread)
# ═══════════════════════════════════════════════════════════════

def run_flask_app(app, host, port, project_name):
    """Run Flask app in a separate thread"""
    try:
        print(f"{Fore.CYAN}[{project_name}] Starting on {host}:{port}...{Style.RESET_ALL}")
        app.run(host=host, port=port, debug=False, use_reloader=False, threaded=True)
    except Exception as e:
        print(f"{Fore.RED}[ERROR] {project_name} failed to start: {e}{Style.RESET_ALL}")

# ═══════════════════════════════════════════════════════════════
# Discord Bot Runner (Async)
# ═══════════════════════════════════════════════════════════════

async def run_discord_bot():
    """Run Discord bot asynchronously"""
    try:
        print(f"{Fore.CYAN}[Discord Bot] Starting...{Style.RESET_ALL}")
        await discord_bot.start(os.getenv("DISCORD_TOKEN"))
    except Exception as e:
        print(f"{Fore.RED}[ERROR] Discord Bot failed to start: {e}{Style.RESET_ALL}")

# ═══════════════════════════════════════════════════════════════
# Main Async Orchestrator
# ═══════════════════════════════════════════════════════════════

def start_flask_servers():
    """Start both Flask servers in separate threads"""
    
    # JWT Token Generator API
    jwt_thread = threading.Thread(
        target=run_flask_app,
        args=(jwt_app, "0.0.0.0", 30326, "JWT Token Generator API"),
        daemon=True
    )
    jwt_thread.start()
    
    # Long Bio API
    bio_thread = threading.Thread(
        target=run_flask_app,
        args=(bio_api_app, "0.0.0.0", 5000, "Long Bio API"),
        daemon=True
    )
    bio_thread.start()
    
    return jwt_thread, bio_thread

async def main():
    """Main async orchestrator"""
    print(f"\n{Fore.GREEN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}    >> STARTING ALL PROJECTS ASYNCHRONOUSLY <<{Style.RESET_ALL}")
    print(f"{Fore.GREEN}{'='*60}{Style.RESET_ALL}\n")
    
    # Start Flask servers in background threads
    print(f"{Fore.YELLOW}[INFO] Starting Flask servers...{Style.RESET_ALL}")
    jwt_thread, bio_thread = start_flask_servers()
    
    # Give Flask servers time to start
    await asyncio.sleep(2)
    
    # Display project status
    print(f"\n{Fore.GREEN}{'='*60}{Style.RESET_ALL}")
    for project_key, config in PROJECTS.items():
        if config["type"] == "flask":
            print(f"{Fore.GREEN}[OK] {config['name']} -> http://0.0.0.0:{config['port']}{Style.RESET_ALL}")
        else:
            print(f"{Fore.GREEN}[OK] {config['name']} -> Starting...{Style.RESET_ALL}")
    print(f"{Fore.GREEN}{'='*60}\n{Style.RESET_ALL}")
    
    # Start Discord bot
    print(f"{Fore.YELLOW}[INFO] Starting Discord bot...{Style.RESET_ALL}\n")
    try:
        await run_discord_bot()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}[INFO] Shutting down gracefully...{Style.RESET_ALL}")
        await discord_bot.close()

# ═══════════════════════════════════════════════════════════════
# Entry Point
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    try:
        print(f"{Fore.CYAN}[STARTUP] Checking environment and dependencies...{Style.RESET_ALL}\n")
        
        # Check for required environment variables
        if not os.getenv("DISCORD_TOKEN"):
            print(f"{Fore.RED}[ERROR] DISCORD_TOKEN not found in .env file{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}[INFO] Please add your Discord token to .env file:{Style.RESET_ALL}")
            print(f"       DISCORD_TOKEN=your_token_here\n")
            sys.exit(1)
        
        print(f"{Fore.GREEN}[STARTUP] All dependencies loaded successfully\n{Style.RESET_ALL}")
        
        # Run async main
        asyncio.run(main())
        
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}[INFO] All projects stopped by user{Style.RESET_ALL}")
        sys.exit(0)
    except Exception as e:
        print(f"{Fore.RED}[CRITICAL ERROR] {e}{Style.RESET_ALL}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
        sys.exit(1)
