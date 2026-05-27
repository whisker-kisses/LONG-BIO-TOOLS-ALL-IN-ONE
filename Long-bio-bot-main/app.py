import discord
from discord.ext import commands
import asyncio
from datetime import datetime
import os
from dotenv import load_dotenv
import aiohttp
from aiohttp import web
import urllib.parse

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
API_URL = "http://localhost:5000/bio_upload"
PORT = int(os.getenv("PORT", 5005))

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

session = None
cooldowns = {}

REGIONS = {
    "BD": ("Bangladesh", "🇧🇩"),
    "ID": ("Indonesia", "🇮🇩"),
    "TH": ("Thailand", "🇹🇭"),
    "IND": ("India", "🇮🇳"),
    "BR": ("Brazil", "🇧🇷"),
    "SG": ("Singapore", "🇸🇬"),
    "PK": ("Pakistan", "🇵🇰"),
    "US": ("United States", "🇺🇸"),
    "MY": ("Malaysia", "🇲🇾"),
    "VN": ("Vietnam", "🇻🇳"),
    "EUROPE": ("Europe", "🇪🇺"),
    "RU": ("Russia", "🇷🇺"),
    "CN": ("China", "🇨🇳"),
    "JP": ("Japan", "🇯🇵"),
    "KR": ("Korea", "🇰🇷"),
}

def format_region(code: str):
    code = code.upper()
    if code in REGIONS:
        name, flag = REGIONS[code]
        return f"{flag} {name}"
    return code

@bot.event
async def on_ready():
    global session
    if session is None:
        session = aiohttp.ClientSession()
    print(f"Logged in as {bot.user}")

@bot.command(name="bio")
async def bio(ctx, access_token: str = None, *, bio_text: str = None):
    if not access_token or not bio_text:
        return await ctx.reply(
            "**Usage:**\n`!bio <access_token> <new bio>`\n\n"
            "**Example:**\n`!bio ABC123 Hello world!`"
        )

    now = datetime.now().timestamp()
    last = cooldowns.get(ctx.author.id, 0)
    if now - last < 30:
        return await ctx.send(
            f"⏳ Please wait **{int(30 - (now - last))}s** before reusing this command.",
            delete_after=6
        )
    cooldowns[ctx.author.id] = now

    try:
        await ctx.message.delete()
    except:
        pass

    await ctx.send("⏳ Updating bio just wait a moment...", delete_after=3)

    # URL encode the bio text
    encoded_bio = urllib.parse.quote(bio_text)
    url = f"{API_URL}?bio={encoded_bio}&access_token={access_token}"

    try:
        async with session.get(url) as resp:
            if resp.status != 200:
                return await ctx.send("❌ API error.", delete_after=6)
            data = await resp.json()

        if not data.get("success", False):
            error_msg = data.get("status", "Unknown error")
            return await ctx.send(f"❌ Failed to update bio: {error_msg}", delete_after=6)

        # Extract user info from response
        user_info = data.get("user_info", {})
        region = user_info.get("server", "UNK")
        
        embed = discord.Embed(
            title="✅ Bio Updated Successfully!",
            color=0x77d5a3,
            description=(
                f"> **Nickname:** {user_info.get('nickname', 'Unknown')}\n"
                f"> **Platform:** {user_info.get('platform', 'Unknown')}\n"
                f"> **Region:** {format_region(region)}\n"
                f"> **Player ID:** {user_info.get('player_id', 'Unknown')}\n"
                f"> **New Bio:** ||{data.get('bio', bio_text)}||\n"
                f"> **Login Method:** {data.get('login_method', 'Unknown')}\n"
                f"> **Timestamp:** {data.get('timestamp', 'Unknown')}"
            )
        )
        embed.set_thumbnail(url=ctx.author.display_avatar.url)
        embed.set_footer(text="DEVELOPED BY Watashii")
        await ctx.send(ctx.author.mention, embed=embed)

    except Exception as e:
        print(f"Error: {e}")
        await ctx.send("❌ Unexpected error occurred.", delete_after=6)

async def start_web_server():
    app = web.Application()
    async def handle(request):
        return web.Response(text="Bot is running ✅")
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    print(f"Web server running on port {PORT}")

async def main():
    await start_web_server()
    async with bot:
        await bot.start(TOKEN)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass