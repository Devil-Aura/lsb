# handlers/genlink.py

from pyrogram import filters
from bot import app
from services.token_system import generate_token
from utils.permissions import is_admin

BASE_URL = "https://yourdomain.com/start?token="

@app.on_message(filters.command("genlink"))
async def gen_link(client, message):
    if not await is_admin(message.from_user.id):
        return

    token = await generate_token(message.from_user.id)
    link = BASE_URL + token

    await message.reply(
        f"Generated Secure Link:\n{link}\n\nValid for 10 minutes."
    )
