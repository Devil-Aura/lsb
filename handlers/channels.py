# handlers/channels.py

from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot import app
from database.mongo import channels
from utils.permissions import is_admin
from utils.token import encode_token

PAGE_SIZE = 5


async def get_channels(page=0):
    chs = await channels.find({}).to_list(length=1000)
    total = len(chs)

    start = page * PAGE_SIZE
    end = start + PAGE_SIZE
    return chs[start:end], total


@app.on_message(filters.command("addchannel"))
async def add_channel(client, message):
    if not await is_admin(message.from_user.id):
        return

    if len(message.command) < 3:
        return await message.reply("Usage: /addchannel Name ChannelID")

    name = message.command[1]
    channel_id = int(message.command[2])

    try:
        member = await client.get_chat_member(channel_id, "me")
        if not member.privileges.can_invite_users:
            return await message.reply("No invite permission.")
    except:
        return await message.reply("Bot not admin in channel.")

    invite = await client.create_chat_invite_link(channel_id)
    primary = invite.invite_link

    await channels.insert_one({
        "name": name,
        "channel_id": channel_id,
        "primary_link": primary
    })

    await message.reply(f"Channel {name} added successfully.")


@app.on_message(filters.command("delchannel"))
async def del_channel(client, message):
    if not await is_admin(message.from_user.id):
        return

    if len(message.command) < 2:
        return await message.reply("Usage: /delchannel channel_id")

    channel_id = int(message.command[1])
    await channels.delete_one({"channel_id": channel_id})
    await message.reply("Channel removed.")


@app.on_message(filters.command("channels"))
async def list_channels(client, message):
    if not await is_admin(message.from_user.id):
        return

    page = 0
    page_data, total = await get_channels(page)

    buttons = []
    text = ""

    for i, ch in enumerate(page_data, start=1):
        request_token = encode_token({
            "channel_id": ch["channel_id"],
            "mode": "request"
        })

        normal_token = encode_token({
            "channel_id": ch["channel_id"],
            "mode": "normal"
        })

        text += (
            f"{i}. {ch['name']}\n"
            f"Primary: {ch['primary_link']}\n"
            f"Request: https://t.me/{(await app.get_me()).username}?start={request_token}\n"
            f"Normal: https://t.me/{(await app.get_me()).username}?start={normal_token}\n\n"
        )

    nav = []
    if total > PAGE_SIZE:
        nav.append(InlineKeyboardButton("Next ▶️", callback_data="channels_page:1"))

    buttons.append(nav)
    buttons.append([InlineKeyboardButton("➕ Add Channel", callback_data="add_channel_ui")])

    await message.reply(text or "No Channels Found.", reply_markup=InlineKeyboardMarkup(buttons))


@app.on_message(filters.command("search"))
async def search_channel(client, message):
    if not await is_admin(message.from_user.id):
        return

    if len(message.command) < 2:
        return await message.reply("Usage: /search name")

    query = message.text.split(None, 1)[1].lower()

    results = await channels.find({
        "name": {"$regex": query, "$options": "i"}
    }).to_list(length=20)

    if not results:
        return await message.reply("No results found.")

    buttons = []
    for ch in results:
        buttons.append([
            InlineKeyboardButton(
                ch["name"],
                callback_data=f"channel_view:{ch['channel_id']}"
            )
        ])

    await message.reply(
        "Here Are Some Search Results 🔎",
        reply_markup=InlineKeyboardMarkup(buttons)
    )
