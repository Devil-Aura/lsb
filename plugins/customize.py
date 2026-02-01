from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from config import Config
from database import db
from helper_func import is_owner_or_admin

@Client.on_message(filters.command("customize") & is_owner_or_admin)
async def customize_menu(client: Client, message: Message):
    buttons = [
        [InlineKeyboardButton("Image Post", callback_data="cust_image"), InlineKeyboardButton("Second Message", callback_data="cust_msg2")],
        [InlineKeyboardButton("Forward", callback_data="cust_fwd"), InlineKeyboardButton("Revoke Time", callback_data="cust_revoke")],
        [InlineKeyboardButton("Close", callback_data="close_menu")]
    ]
    await message.reply_text("Customize Bot Settings:", reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_callback_query(filters.regex("cust_image"))
async def cust_image(client: Client, callback_query: CallbackQuery):
    buttons = [
        [InlineKeyboardButton("Set Caption", callback_data="set_caption"), InlineKeyboardButton("Set Image", callback_data="set_image")],
        [InlineKeyboardButton("Set Button Text", callback_data="set_btn_text"), InlineKeyboardButton("Back", callback_data="back_to_main")]
    ]
    await callback_query.message.edit_text("Customize Image Post:", reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_callback_query(filters.regex("back_to_main"))
async def back_to_main(client: Client, callback_query: CallbackQuery):
    await customize_menu(client, callback_query.message)

@Client.on_callback_query(filters.regex("close_menu"))
async def close_menu(client: Client, callback_query: CallbackQuery):
    await callback_query.message.delete()

# --- Placeholder for Setters (Using message listener in real implementation) ---
# For simplicity in this prompt response, I'm setting up the structure.
# Real implementation would use client.ask or a state machine.

@Client.on_callback_query(filters.regex("set_caption"))
async def set_caption_prompt(client: Client, callback_query: CallbackQuery):
    await callback_query.message.reply_text("Send new caption (Use /setcaption [text] for now).")

@Client.on_message(filters.command("setcaption") & is_owner_or_admin)
async def set_caption_cmd(client: Client, message: Message):
    if len(message.command) < 2:
        return
    text = message.text.split(None, 1)[1]
    await db.update_setting("caption", text)
    await message.reply_text("Caption updated.")

@Client.on_message(filters.command("setimage") & is_owner_or_admin)
async def set_image_cmd(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: /setimage [url]")
    url = message.command[1]
    await db.update_setting("image_post", url)
    await message.reply_text("Image URL updated.")
