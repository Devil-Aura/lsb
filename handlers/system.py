# handlers/system.py

import time
import psutil
import platform
from datetime import datetime
from pyrogram import filters
from bot import app
from database.mongo import users, settings
from utils.permissions import is_admin

START_TIME = time.time()

# ================= PING =================

@app.on_message(filters.command("ping"))
async def ping_handler(client, message):
    start = time.time()
    m = await message.reply("Pinging...")
    end = time.time()

    latency = round((end - start) * 1000, 2)
    await m.edit(f"Pong! {latency} ms")

# ================= STATUS =================

@app.on_message(filters.command("status"))
async def status_handler(client, message):
    if not await is_admin(message.from_user.id):
        return

    total_users = await users.count_documents({})
    uptime = str(datetime.now() - datetime.fromtimestamp(START_TIME)).split(".")[0]

    text = f"""
Bot Status

Users: {total_users}
Uptime: {uptime}
CPU Usage: {psutil.cpu_percent()}%
RAM Usage: {psutil.virtual_memory().percent}%
Python: {platform.python_version()}
System: {platform.system()}
"""

    await message.reply(text)

# ================= BACKUP =================

@app.on_message(filters.command("backup"))
async def backup_handler(client, message):
    if not await is_admin(message.from_user.id):
        return

    data = {
        "users": [u async for u in users.find({})],
        "settings": await settings.find_one({"_id": "main"})
    }

    file_name = "backup.json"
    with open(file_name, "w") as f:
        import json
        json.dump(data, f, indent=2)

    await message.reply_document(file_name)
