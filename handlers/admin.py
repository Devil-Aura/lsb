# handlers/admin.py

from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot import app
from database.mongo import admins
from utils.permissions import is_admin

PAGE_SIZE = 5


async def get_admins(page=0):
    cursor = admins.find({})
    admins_list = await cursor.to_list(length=1000)
    total = len(admins_list)

    start = page * PAGE_SIZE
    end = start + PAGE_SIZE
    return admins_list[start:end], total


@app.on_message(filters.command("addadmin"))
async def add_admin(client, message):
    if not await is_admin(message.from_user.id):
        return

    if len(message.command) < 2:
        return await message.reply("Usage: /addadmin user_id")

    user_id = int(message.command[1])

    if await admins.find_one({"user_id": user_id}):
        return await message.reply("Already admin.")

    await admins.insert_one({"user_id": user_id})
    await message.reply(f"Successfully added {user_id} as admin.")


@app.on_message(filters.command("deladmin"))
async def del_admin(client, message):
    if not await is_admin(message.from_user.id):
        return

    if len(message.command) < 2:
        return await message.reply("Usage: /deladmin user_id")

    user_id = int(message.command[1])
    await admins.delete_one({"user_id": user_id})
    await message.reply("Admin removed.")


@app.on_message(filters.command("admins"))
async def list_admins(client, message):
    if not await is_admin(message.from_user.id):
        return

    page = 0
    admins_page, total = await get_admins(page)

    buttons = []
    for adm in admins_page:
        buttons.append([
            InlineKeyboardButton(
                f"Admin {adm['user_id']}",
                callback_data=f"view_admin:{adm['user_id']}"
            )
        ])

    nav = []
    if total > PAGE_SIZE:
        nav.append(InlineKeyboardButton("Next ▶️", callback_data="admins_page:1"))

    buttons.append(nav)
    buttons.append([InlineKeyboardButton("➕ Add Admin", callback_data="add_admin_ui")])

    await message.reply(
        f"Admins List (Total: {total})",
        reply_markup=InlineKeyboardMarkup(buttons)
    )
