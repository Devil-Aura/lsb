import time
import shutil
import psutil
from pyrogram import Client, filters
from pyrogram.types import Message
from config import Config
from database import db
from helper_func import is_owner_or_admin, get_readable_time

START_TIME = time.time()

@Client.on_message(filters.command(["status", "ping"]) & is_owner_or_admin)
async def status_command(client: Client, message: Message):
    uptime = get_readable_time(time.time() - START_TIME)
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory().percent
    disk = psutil.disk_usage("/").percent
    
    text = f"""
⚙️ **SYSTEM STATUS**

🖥 CPU: {cpu}% | RAM: {mem}% | DISK: {disk}%
⏱ Uptime: {uptime}
    """
    await message.reply_text(text)
