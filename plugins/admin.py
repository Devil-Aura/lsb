# +++ Modified By [telegram username: @Codeflix_Bots]

import math
from pyrogram import Client, filters
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery
)
from config import OWNER_ID
from database.database import add_admin, remove_admin, list_admins

ADMINS_PER_PAGE = 6
ADD_ADMIN_STATE = {}

# ─────────────────────────────
# Helpers
# ─────────────────────────────

async def get_user_display(client, user_id: int):
    try:
        user = await client.get_users(user_id)
        name = user.first_name or "Unknown"
        username = f"@{user.username}" if user.username else "None"
        return name, username
    except:
        return "Unknown", "None"


def build_admin_keyboard(admins, page: int):
    start = page * ADMINS_PER_PAGE
    end = start + ADMINS_PER_PAGE
    sliced = admins[start:end]

    buttons = []

    # Admin buttons
    for uid in sliced:
        buttons.append([
            InlineKeyboardButton(
                text=f"👤 {uid}",
                callback_data=f"admin_view:{uid}:{page}"
            )
        ])

    # ➕ Add Admin button
    buttons.append([
        InlineKeyboardButton("➕ Add Admin", callback_data="admin_add")
    ])

    # Navigation
    nav = []
    if page > 0:
        nav.append(
            InlineKeyboardButton("⬅️ Prev", callback_data=f"admin_page:{page-1}")
        )
    if end < len(admins):
        nav.append(
            InlineKeyboardButton("➡️ Next", callback_data=f"admin_page:{page+1}")
        )

    if nav:
        buttons.append(nav)

    return InlineKeyboardMarkup(buttons)


# ─────────────────────────────
# /admins command
# ─────────────────────────────

@Client.on_message(filters.command("admins") & filters.user(OWNER_ID))
async def admins_command(client, message: Message):
    admins = await list_admins()
    if not admins:
        return await message.reply_text("❌ No admins found.")

    await message.reply_text(
        "👮 <b>Admins List</b>",
        reply_markup=build_admin_keyboard(admins, 0)
    )


# ─────────────────────────────
# Pagination handler
# ─────────────────────────────

@Client.on_callback_query(filters.regex("^admin_page:"))
async def admin_page_cb(client, query: CallbackQuery):
    page = int(query.data.split(":")[1])
    admins = await list_admins()

    await query.message.edit_text(
        "👮 <b>Admins List</b>",
        reply_markup=build_admin_keyboard(admins, page)
    )
    await query.answer()


# ─────────────────────────────
# Admin detail view
# ─────────────────────────────

@Client.on_callback_query(filters.regex("^admin_view:"))
async def admin_view_cb(client, query: CallbackQuery):
    _, user_id, page = query.data.split(":")
    user_id = int(user_id)

    name, username = await get_user_display(client, user_id)

    text = (
        "<b>👤 Admin Details</b>\n\n"
        f"• <b>Name:</b> {name}\n"
        f"• <b>User ID:</b> <code>{user_id}</code>\n"
        f"• <b>Username:</b> {username}"
    )

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "❌ Remove Admin",
                callback_data=f"admin_remove:{user_id}:{page}"
            )
        ],
        [
            InlineKeyboardButton(
                "🔙 Back",
                callback_data=f"admin_page:{page}"
            )
        ]
    ])

    await query.message.edit_text(text, reply_markup=keyboard)
    await query.answer()


# ─────────────────────────────
# Remove admin
# ─────────────────────────────

@Client.on_callback_query(filters.regex("^admin_remove:"))
async def admin_remove_cb(client, query: CallbackQuery):
    _, user_id, page = query.data.split(":")
    user_id = int(user_id)
    page = int(page)

    await remove_admin(user_id)
    admins = await list_admins()

    await query.message.edit_text(
        "✅ <b>Admin removed successfully.</b>",
        reply_markup=build_admin_keyboard(admins, max(page - 1, 0))
    )
    await query.answer("Admin removed")


# ─────────────────────────────
# Add admin flow
# ─────────────────────────────

@Client.on_callback_query(filters.regex("^admin_add$"))
async def admin_add_cb(client, query: CallbackQuery):
    ADD_ADMIN_STATE[query.from_user.id] = True
    await query.message.reply_text(
        "🆔 <b>Send the User ID to add as admin</b>"
    )
    await query.answer()


@Client.on_message(filters.private & filters.user(OWNER_ID))
async def add_admin_input(client, message: Message):
    if not ADD_ADMIN_STATE.get(message.from_user.id):
        return

    if not message.text.isdigit():
        return await message.reply_text("❌ Please send a valid numeric user ID.")

    user_id = int(message.text)
    await add_admin(user_id)

    name, _ = await get_user_display(client, user_id)

    ADD_ADMIN_STATE.pop(message.from_user.id, None)

    await message.reply_text(
        f"✅ <b>Successfully added admin</b>\n\n"
        f"• <b>Name:</b> {name}\n"
        f"• <b>User ID:</b> <code>{user_id}</code>"
    )


# ─────────────────────────────
# /addadmin command
# ─────────────────────────────

@Client.on_message(filters.command("addadmin") & filters.user(OWNER_ID))
async def add_admin_command(client, message: Message):
    if len(message.command) != 2 or not message.command[1].isdigit():
        return await message.reply_text("Usage: <code>/addadmin user_id</code>")

    user_id = int(message.command[1])
    await add_admin(user_id)

    await message.reply_text(f"✅ Admin added: <code>{user_id}</code>")


# ─────────────────────────────
# /deladmin command
# ─────────────────────────────

@Client.on_message(filters.command("deladmin") & filters.user(OWNER_ID))
async def del_admin_command(client, message: Message):
    if len(message.command) != 2 or not message.command[1].isdigit():
        return await message.reply_text("Usage: <code>/deladmin user_id</code>")

    user_id = int(message.command[1])
    await remove_admin(user_id)

    await message.reply_text(f"✅ Admin removed: <code>{user_id}</code>")
