# handlers/public.py

import asyncio
from datetime import datetime
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot import app
from config import START_DATE
from database.mongo import users, settings, channels, force_sub
from utils.token import decode_token
from utils.invite import get_or_create_invite
from utils.scheduler import delete_after_delay
from utils.permissions import is_admin


# ================= SETTINGS =================

async def get_settings():
    s = await settings.find_one({"_id": "main"})
    if not s:
        default = {
            "_id": "main",
            "revoke_time": 1800,
            "delete_time": 1740,
            "button_text": "⛩️ 𝗖𝗟𝗜𝗖𝗞 𝗛𝗘𝗥𝗘 𝗧𝗢 𝗝𝗢𝗜𝗡 ⛩️",
            "caption": "Channel link 🔗 👇👇\n\n[link]\n[link]",
            "second_message": "Please Join The Channel By Clicking The Link Or Button And This Link Will Expire within few minutes.",
            "second_enabled": True,
            "forward_enabled": True,
            "maintenance": False,
            "force_enabled": False
        }
        await settings.insert_one(default)
        return default
    return s


async def store_user(user_id: int):
    if not await users.find_one({"_id": user_id}):
        await users.insert_one({"_id": user_id})


# ================= FORCE SUB CORE =================

async def check_force_sub(app, user_id: int):
    s = await get_settings()
    if not s["force_enabled"]:
        return True

    channels_list = force_sub.find({})
    not_joined = []

    async for ch in channels_list:
        try:
            member = await app.get_chat_member(ch["channel_id"], user_id)
            if member.status in ["left", "kicked"]:
                not_joined.append(ch)
        except:
            not_joined.append(ch)

    if not_joined:
        return not_joined

    return True


async def send_force_sub_message(message, channels_list):
    buttons = []
    for ch in channels_list:
        invite = await get_or_create_invite(
            app,
            ch["channel_id"],
            ch.get("request_mode", False),
            300
        )
        buttons.append([InlineKeyboardButton(ch["name"], url=invite)])

    retry = InlineKeyboardButton(
        "🔁 Retry",
        url=f"https://t.me/{(await app.get_me()).username}?start=start"
    )
    buttons.append([retry])

    await message.reply(
        "<b>ʀᴏᴋᴏ!</b>\n\n<b>Please Join All Required Channels To Continue.</b>",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


# ================= START =================

@app.on_message(filters.command("start"))
async def start_handler(client, message):
    s = await get_settings()

    if s["maintenance"]:
        return await message.reply(
            "The Bot Is Under Maintenance After Few Time Bot Will Back To Work As Before."
        )

    await store_user(message.from_user.id)

    # NORMAL START
    if len(message.command) == 1:
        text = (
            "<b>"
            "Konnichiwa! 🤗\n\n"
            "Mera Naam <b>Crunchyroll Link Provider</b> hai.\n\n"
            "Main aapko <b>anime channels</b> ki links provide karta hu.\n\n"
            "<blockquote>"
            "🔹 Agar aapko kisi anime ki link chahiye,<br>"
            "🔹 Ya channel ki link nahi mil rahi hai,<br>"
            "🔹 Ya link expired ho gayi hai"
            "</blockquote>\n\n"
            "Toh <b>@CrunchyRollChannel</b> se New aur working links le sakte hain.\n\n"
            "Shukriya! ❤️"
            "</b>"
        )

        msg = await message.reply(text)
        asyncio.create_task(
            delete_after_delay(app, message.chat.id, [msg.id], 900)
        )
        return

    # TOKEN START
    token = message.command[1]
    try:
        data = decode_token(token)
    except:
        return await message.reply("Invalid Link.")

    channel_id = data["channel_id"]
    request_mode = data["mode"] == "request"

    # FORCE SUB CHECK
    fs_check = await check_force_sub(app, message.from_user.id)
    if fs_check is not True:
        return await send_force_sub_message(message, fs_check)

    revoke_time = s["revoke_time"]
    delete_time = s["delete_time"]

    invite_link = await get_or_create_invite(
        app,
        channel_id,
        request_mode,
        revoke_time
    )

    caption = s["caption"].replace("[link]", invite_link)

    button = InlineKeyboardMarkup([
        [InlineKeyboardButton(s["button_text"], url=invite_link)]
    ])

    image_msg = await message.reply_photo(
        photo=s.get("image_file_id", "https://via.placeholder.com/600x400"),
        caption=caption,
        reply_markup=button
    )

    msg_ids = [image_msg.id]

    if s["second_enabled"]:
        second = await image_msg.reply(s["second_message"])
        msg_ids.append(second.id)

    asyncio.create_task(
        delete_after_delay(app, message.chat.id, msg_ids, delete_time)
    )


# ================= HELP =================

@app.on_message(filters.command("help"))
async def help_handler(client, message):
    text = (
        "<blockquote expandable>"
        "<b>🆘 Help & Support</b>\n"
        "Agar aapko kisi bhi help ki zaroorat hai, toh humse yahan sampark karein:\n"
        "<b>@CrunchyRollHelper</b>"
        "</blockquote>\n\n"
        "<b>🎬 More Anime</b>\n"
        "Agar aap aur anime dekna chahte hain, toh yahan se dekh sakte hain:\n"
        "<b>@CrunchyRollChannel</b>\n\n"
        "<blockquote expandable>"
        "<b>🤖 Bot Info</b>\n"
        "Bot ki jaankari ke liye /about ya /info ka istemal karein."
        "</blockquote>"
    )

    msg = await message.reply(text)
    asyncio.create_task(
        delete_after_delay(app, message.chat.id, [msg.id], 120)
    )


# ================= ABOUT =================

@app.on_message(filters.command(["about", "info"]))
async def about_handler(client, message):
    start_date = datetime.strptime(START_DATE, "%Y-%m-%d")
    age = datetime.utcnow() - start_date

    text = (
        "About The Bot\n\n"
        "🤖 My Name :- <a href='https://telegra.ph/Crunchy-Roll-Vault-04-08'>Crunchyroll Link Provider</a>\n\n"
        f"Bot Age :- {age.days} Days\n"
        "Anime Channel :- <a href='https://t.me/Crunchyrollchannel'>Crunchy Roll Channel</a>\n"
        "Language :- <a href='https://t.me/Crunchyrollchannel'>Python</a>\n"
        "Developer :- <a href='https://t.me/World_Fastest_Bots'>World Fastest Bots</a>\n\n"
        "This Is Private/Paid Bot Provided By @World_Fastest_Bots."
    )

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("📡 𝗣𝗼𝘄𝗲𝗿𝗲𝗱 𝗕𝘆", url="https://t.me/World_Fastest_Bots")],
        [InlineKeyboardButton("World Fastest Bots", url="https://t.me/World_Fastest_Bots")]
    ])

    msg = await message.reply(text, reply_markup=buttons)
    asyncio.create_task(
        delete_after_delay(app, message.chat.id, [msg.id], 60)
    )
