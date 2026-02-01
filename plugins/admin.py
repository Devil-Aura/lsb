from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from config import Config
from database import db
from helper_func import is_owner_or_admin

@Client.on_message(filters.command("addadmin") & filters.user(Config.OWNER_ID))
async def add_admin(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: /addadmin [user_id]")
    
    try:
        user_id = int(message.command[1])
        if await db.add_admin(user_id):
            await message.reply_text(f"Successfully added admin: {user_id}")
        else:
            await message.reply_text("User is already an admin.")
    except ValueError:
        await message.reply_text("Invalid User ID.")

@Client.on_message(filters.command("deladmin") & filters.user(Config.OWNER_ID))
async def del_admin(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: /deladmin [user_id]")
    
    try:
        user_id = int(message.command[1])
        if await db.remove_admin(user_id):
            await message.reply_text(f"Successfully removed admin: {user_id}")
        else:
            await message.reply_text("User is not an admin.")
    except ValueError:
        await message.reply_text("Invalid User ID.")

@Client.on_message(filters.command("admins") & filters.user(Config.OWNER_ID))
async def list_admins(client: Client, message: Message):
    admins = await db.get_admins()
    if not admins:
        return await message.reply_text("No admins found.")
    
    # Pagination Logic could be here, but for simplicity assuming < 100 admins for now
    buttons = []
    for admin_id in admins:
        buttons.append([InlineKeyboardButton(f"Admin: {admin_id}", callback_data=f"admin_info_{admin_id}")])
    
    buttons.append([InlineKeyboardButton("➕ Add Admin", callback_data="add_new_admin")])
    
    await message.reply_text("List of Admins:", reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_callback_query(filters.regex(r"^admin_info_"))
async def admin_info_callback(client: Client, callback_query: CallbackQuery):
    admin_id = int(callback_query.data.split("_")[2])
    
    buttons = [
        [InlineKeyboardButton("Remove Admin", callback_data=f"remove_admin_{admin_id}")],
        [InlineKeyboardButton("Back", callback_data="back_to_admins")]
    ]
    
    await callback_query.message.edit_text(
        f"Admin Info:\nID: {admin_id}",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@Client.on_callback_query(filters.regex(r"^remove_admin_"))
async def remove_admin_callback(client: Client, callback_query: CallbackQuery):
    admin_id = int(callback_query.data.split("_")[2])
    await db.remove_admin(admin_id)
    await callback_query.answer("Admin removed successfully.")
    await list_admins(client, callback_query.message) # Refresh list

@Client.on_callback_query(filters.regex("back_to_admins"))
async def back_to_admins_callback(client: Client, callback_query: CallbackQuery):
    await list_admins(client, callback_query.message)

@Client.on_callback_query(filters.regex("add_new_admin"))
async def add_new_admin_callback(client: Client, callback_query: CallbackQuery):
    await callback_query.message.edit_text("Send User ID to add as admin (Use /addadmin command directly for now).")
