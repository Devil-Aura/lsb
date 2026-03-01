# handlers/stats.py

from pyrogram import filters
from bot import app
from database.mongo import users, channels, invites
from utils.permissions import is_admin


@app.on_message(filters.command("stats"))
async def stats_handler(client, message):
    if not await is_admin(message.from_user.id):
        return

    total_users = await users.count_documents({})
    total_channels = await channels.count_documents({})
    total_links = await invites.count_documents({})

    await message.reply(
        f"📊 Stats\n\n"
        f"Total Users: {total_users}\n"
        f"Total Channels: {total_channels}\n"
        f"Total Active Links: {total_links}"
    )
