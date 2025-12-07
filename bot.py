import os
import time
import random
import asyncio
import aiohttp.web
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from catboxpy.catbox import CatboxClient
import litterbox_uploader as litterbox

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

MAX_PERMANENT = 200 * 1024 * 1024      # 200MB
MAX_TEMPORARY = 1024 * 1024 * 1024     # 1GB

CACHE = {}
CACHE_TIMEOUT = 600

catbox = CatboxClient()

# ------------------ CACHE CLEANER ------------------
async def cache_cleaner():
    while True:
        now = time.time()
        expired = [k for k, v in CACHE.items() if now - v["time"] > CACHE_TIMEOUT]
        for k in expired:
            del CACHE[k]
        await asyncio.sleep(60)

# ------------------ BOT CLASS ------------------
class FileToLinkBot(Client):
    async def start(self):
        await super().start()
        print("Bot started successfully.")
        asyncio.create_task(cache_cleaner())

bot = FileToLinkBot(
    "filetolinkbot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    workers=40,
    max_concurrent_transmissions=20,
    in_memory=True
)

# ------------------ /start COMMAND ------------------
@bot.on_message(filters.command("start"))
async def start_cmd(client, message):
    buttons = [
        [
            InlineKeyboardButton("📢 Updates", url="https://t.me/Granny_Bots"),
            InlineKeyboardButton("👤 Owner", user_id=6658060675)
        ]
    ]

    text = (
        f"👋 **Welcome to {client.me.mention}!**\n\n"
        f"Send me **any file (image/video/doc)** and I will give you a direct link.\n\n"
        f"🔗 Permanent uploads → **200MB**\n"
        f"⏳ Temporary uploads → **1GB**\n\n"
        f"👨‍💻 Created by: @Granny_Bots"
    )

    await message.reply(text, reply_markup=InlineKeyboardMarkup(buttons))

# ------------------ FILE RECEIVED ------------------
@bot.on_message(filters.private & filters.media)
async def ask_service(client, message):

    media = (
        message.document or message.video or
        message.photo or message.animation or
        message.audio or message.voice
    )

    if not media:
        return await message.reply("⚠ Unsupported file type.")

    if media.file_size > MAX_TEMPORARY:
        return await message.reply("❌ Temporary upload limit: **1GB**")

    CACHE[message.id] = {
        "file_id": media.file_id,
        "file_size": media.file_size,
        "time": time.time()
    }

    buttons = [
        [InlineKeyboardButton("Permanent (200MB)", callback_data=f"perm:{message.id}")],
        [InlineKeyboardButton("Temporary (1GB)", callback_data=f"temp:{message.id}")]
    ]

    await message.reply(
        "📤 **Choose upload type:**",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# ------------------ PERMANENT UPLOAD ------------------
@bot.on_callback_query(filters.regex(r"^perm:(\d+)$"))
async def permanent_handler(client, cq):

    key = int(cq.data.split(":")[1])
    if key not in CACHE:
        return await cq.message.edit("❌ Cache expired.")

    data = CACHE[key]

    if data["file_size"] > MAX_PERMANENT:
        return await cq.message.edit("❌ Permanent limit is **200MB**.")

    await cq.message.edit("⬇️ Downloading…")

    file_path = await client.download_media(data["file_id"])

    try:
        url = catbox.upload(file_path)
        await cq.message.edit(f"✅ **Uploaded!**\n{url}")
    except Exception as e:
        await cq.message.edit(f"❌ Upload failed:\n`{e}`")

    if os.path.exists(file_path):
        os.remove(file_path)

# ------------------ TEMPORARY TIME SELECT ------------------
@bot.on_callback_query(filters.regex(r"^temp:(\d+)$"))
async def select_time(client, cq):

    key = int(cq.data.split(":")[1])
    if key not in CACHE:
        return await cq.message.edit("❌ Cache expired.")

    buttons = [
        [
            InlineKeyboardButton("1h", callback_data=f"lit:{key}:1h"),
            InlineKeyboardButton("12h", callback_data=f"lit:{key}:12h")
        ],
        [
            InlineKeyboardButton("24h", callback_data=f"lit:{key}:24h"),
            InlineKeyboardButton("72h", callback_data=f"lit:{key}:72h")
        ]
    ]

    await cq.message.edit(
        "⏳ **Select expiry time:**",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# ------------------ TEMPORARY UPLOAD ------------------
@bot.on_callback_query(filters.regex(r"^lit:(\d+):(.*)$"))
async def temporary_handler(client, cq):

    _, key, timeout = cq.data.split(":")
    key = int(key)

    if key not in CACHE:
        return await cq.message.edit("❌ Cache expired.")

    await cq.message.edit("⬇️ Downloading…")

    data = CACHE[key]
    file_path = await client.download_media(data["file_id"])

    try:
        url = litterbox.upload(file_path, time=timeout)
        await cq.message.edit(f"✅ **Uploaded!**\n⏳ Expires in {timeout}\n{url}")
    except Exception as e:
        await cq.message.edit(f"❌ Upload failed:\n`{e}`")

    if os.path.exists(file_path):
        os.remove(file_path)

# ------------------ RUN BOT ------------------
'''
Use bot.run() and remove other health check system if you're using Dockerfile
if using render service or any other web service then leave it as it is as it will work.
'''
#bot.run()

async def health_check_handler(request):
    return aiohttp.web.Response(text="Bot is running")

async def start_web_server():
    port = int(os.environ.get("PORT", 8080)) 
    server_app = aiohttp.web.Application()
    server_app.add_routes([aiohttp.web.get('/health', health_check_handler)])
    
    runner = aiohttp.web.AppRunner(server_app)
    await runner.setup()
    site = aiohttp.web.TCPSite(runner, '0.0.0.0', port)
    print(f"Starting health check web server on port {port}...")
    await site.start()
    
    while True:
        await asyncio.sleep(3600)

async def start_bot():
    print("Starting Telegram bot client...")
    
    try:
        await bot.start()
        print("Pyrofork client started. Running indefinitely...")
        while True:
            await asyncio.sleep(3600)

    except Exception as e:
        print(f"An error occurred in start_bot: {e}")
    
    finally:
        print("Stopping Pyrofork client...")
        await bot.stop()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    
    tasks = [
        start_web_server(),
        start_bot()
    ]
    
    loop.run_until_complete(asyncio.gather(*tasks))
