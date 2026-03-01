# handlers/customize.py

from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot import app
from database.mongo import settings, force_sub
from utils.permissions import is_admin

# ================= UTIL =================

async def get_settings():
    return await settings.find_one({"_id": "main"})

async def update_setting(key, value):
    await settings.update_one(
        {"_id": "main"},
        {"$set": {key: value}},
        upsert=True
    )

def back_close():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⬅️ Back", callback_data="customize_main"),
            InlineKeyboardButton("❌ Close", callback_data="close_panel")
        ]
    ])

# ================= MAIN PANEL =================

@app.on_message(filters.command("customize"))
async def customize_panel(client, message):
    if not await is_admin(message.from_user.id):
        return

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🖼 Image Post", callback_data="cust_image")],
        [InlineKeyboardButton("💬 Second Message", callback_data="cust_second")],
        [InlineKeyboardButton("📤 Forward", callback_data="cust_forward")],
        [InlineKeyboardButton("⏳ Revoke Time", callback_data="cust_time")],
        [InlineKeyboardButton("📢 Force Sub", callback_data="cust_force")],
        [InlineKeyboardButton("🛠 Maintenance Mode", callback_data="cust_maint")]
    ])

    await message.reply(
        "Here you can customise all the things of bot.",
        reply_markup=buttons
    )

# ================= IMAGE SYSTEM =================

@app.on_callback_query(filters.regex("cust_image"))
async def image_menu(client, query):
    s = await get_settings()
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("📸 Current Image", callback_data="img_current")],
        [InlineKeyboardButton("✅ Set Image", callback_data="img_set")],
        [InlineKeyboardButton("🗑 Delete Image", callback_data="img_delete")],
        [InlineKeyboardButton("✏️ Caption", callback_data="img_caption")],
        [InlineKeyboardButton("🔘 Button Text", callback_data="img_button")],
        [
            InlineKeyboardButton("⬅️ Back", callback_data="customize_main"),
            InlineKeyboardButton("❌ Close", callback_data="close_panel")
        ]
    ])

    await query.message.edit(
        "Here you can customise Image Post Message",
        reply_markup=buttons
    )

# ================= SET IMAGE =================

image_waiting = {}

@app.on_callback_query(filters.regex("img_set"))
async def set_image(client, query):
    image_waiting[query.from_user.id] = True
    await query.message.edit(
        "Please send new image which you want to set.",
        reply_markup=back_close()
    )

@app.on_message(filters.photo)
async def receive_image(client, message):
    if message.from_user.id not in image_waiting:
        return

    file_id = message.photo.file_id
    await update_setting("image_file_id", file_id)
    image_waiting.pop(message.from_user.id)

    await message.reply(
        "Image successfully set.",
        reply_markup=back_close()
    )

# ================= CAPTION SYSTEM =================

caption_waiting = {}

@app.on_callback_query(filters.regex("img_caption"))
async def caption_menu(client, query):
    s = await get_settings()
    caption_waiting[query.from_user.id] = True

    await query.message.edit(
        f"Current Caption:\n\n{s['caption']}\n\nUse [link] in caption for link position.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Set Caption", callback_data="caption_set")],
            [InlineKeyboardButton("⬅️ Back", callback_data="cust_image")]
        ])
    )

@app.on_callback_query(filters.regex("caption_set"))
async def caption_set_wait(client, query):
    await query.message.reply("Send new caption.")

@app.on_message(filters.text)
async def receive_caption(client, message):
    if message.from_user.id not in caption_waiting:
        return

    await update_setting("caption", message.text)
    caption_waiting.pop(message.from_user.id)

    await message.reply(
        "New caption set successfully.",
        reply_markup=back_close()
    )

# ================= BUTTON TEXT =================

button_waiting = {}

@app.on_callback_query(filters.regex("img_button"))
async def button_text_menu(client, query):
    s = await get_settings()
    await query.message.edit(
        f"Current Button Text:\n{s['button_text']}",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Set Button Text", callback_data="btn_set")],
            [InlineKeyboardButton("Delete Button", callback_data="btn_delete")],
            [InlineKeyboardButton("⬅️ Back", callback_data="cust_image")]
        ])
    )

@app.on_callback_query(filters.regex("btn_set"))
async def btn_wait(client, query):
    button_waiting[query.from_user.id] = True
    await query.message.reply("Send new button text.")

@app.on_message(filters.text)
async def receive_button_text(client, message):
    if message.from_user.id not in button_waiting:
        return

    await update_setting("button_text", message.text)
    button_waiting.pop(message.from_user.id)

    await message.reply(
        "Button text updated.",
        reply_markup=back_close()
    )

@app.on_callback_query(filters.regex("btn_delete"))
async def delete_button(client, query):
    await update_setting("button_text", "")
    await query.message.edit(
        "Button deleted successfully.",
        reply_markup=back_close()
    )

# ================= SECOND MESSAGE =================

second_waiting = {}

@app.on_callback_query(filters.regex("cust_second"))
async def second_menu(client, query):
    s = await get_settings()

    await query.message.edit(
        "Here you can customize The second message.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Current Message", callback_data="sec_current")],
            [InlineKeyboardButton("Set New Message", callback_data="sec_set")],
            [InlineKeyboardButton("Toggle On/Off", callback_data="sec_toggle")],
            back_close().inline_keyboard[0]
        ])
    )

@app.on_callback_query(filters.regex("sec_set"))
async def sec_set(client, query):
    second_waiting[query.from_user.id] = True
    await query.message.reply("Send new second message.")

@app.on_message(filters.text)
async def receive_second_message(client, message):
    if message.from_user.id not in second_waiting:
        return

    await update_setting("second_message", message.text)
    second_waiting.pop(message.from_user.id)

    await message.reply(
        "Second message updated.",
        reply_markup=back_close()
    )

@app.on_callback_query(filters.regex("sec_toggle"))
async def toggle_second(client, query):
    s = await get_settings()
    await update_setting("second_enabled", not s["second_enabled"])

    await query.message.edit(
        f"Second Message is now {'ON' if not s['second_enabled'] else 'OFF'}",
        reply_markup=back_close()
    )

# ================= MAINTENANCE =================

@app.on_callback_query(filters.regex("cust_maint"))
async def maintenance_toggle(client, query):
    s = await get_settings()
    new = not s["maintenance"]
    await update_setting("maintenance", new)

    await query.message.edit(
        f"Maintenance Mode is now {'ON' if new else 'OFF'}",
        reply_markup=back_close()
    )

# ================= FORCE SUB =================

@app.on_callback_query(filters.regex("cust_force"))
async def force_menu(client, query):
    s = await get_settings()

    await query.message.edit(
        "Here you can customise force sub.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("On", callback_data="force_on")],
            [InlineKeyboardButton("Off", callback_data="force_off")],
            [InlineKeyboardButton("Force Sub Channels", callback_data="force_channels")],
            [InlineKeyboardButton("Force Sub Message", callback_data="force_msg")],
            back_close().inline_keyboard[0]
        ])
    )

@app.on_callback_query(filters.regex("force_on"))
async def force_on(client, query):
    await update_setting("force_enabled", True)
    await query.message.edit("Force Sub Enabled.", reply_markup=back_close())

@app.on_callback_query(filters.regex("force_off"))
async def force_off(client, query):
    await update_setting("force_enabled", False)
    await query.message.edit("Force Sub Disabled.", reply_markup=back_close())

@app.on_callback_query(filters.regex("force_channels"))
async def force_channels_menu(client, query):
    await query.message.edit(
        "Send channel ID to add force sub channel.",
        reply_markup=back_close()
    )

@app.on_message(filters.text)
async def receive_force_channel(client, message):
    if not await is_admin(message.from_user.id):
        return

    if message.text.startswith("-100"):
        await force_sub.insert_one({
            "channel_id": int(message.text),
            "request_mode": False
        })
        await message.reply("Force sub channel added.", reply_markup=back_close())

@app.on_callback_query(filters.regex("force_msg"))
async def force_msg_menu(client, query):
    await query.message.edit(
        "Send new Force Sub message.",
        reply_markup=back_close()
    )

# ================= CLOSE =================

@app.on_callback_query(filters.regex("close_panel"))
async def close_panel(client, query):
    await query.message.delete()
