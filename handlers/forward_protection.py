# handlers/forward_protection.py

from pyrogram import filters
from bot import app
from database.mongo import settings

@app.on_message(filters.private & filters.forwarded)
async def block_forwarded(client, message):
    s = await settings.find_one({"_id": "main"})
    if s.get("forward_protect", False):
        await message.delete()
        await message.reply("Forwarded messages are not allowed.")
