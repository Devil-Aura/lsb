from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import OWNER_ID
from database.database import is_admin, get_config, set_config, add_fsub, del_fsub, get_fsub_channels
from helper_func import get_seconds

@Client.on_message(filters.command("customize") & filters.private)
async def customize_menu(client, message):
    if not await is_admin(message.from_user.id) and message.from_user.id != OWNER_ID: return
    
    btns = InlineKeyboardMarkup([
        [InlineKeyboardButton("🖼 Image Post", callback_data="set_img"),
         InlineKeyboardButton("📩 Second Msg", callback_data="set_sec")],
        [InlineKeyboardButton("⏳ Timers", callback_data="set_time"),
         InlineKeyboardButton("📢 Force Sub", callback_data="set_fsub")],
        [InlineKeyboardButton("🚧 Maintenance", callback_data="set_maint"),
         InlineKeyboardButton("❌ Close", callback_data="close")]
    ])
    await message.reply("⚙️ <b>Customization Panel</b>", reply_markup=btns)

@Client.on_callback_query(filters.regex("^set_"))
async def settings_cb(client, callback):
    data = callback.data
    user_id = callback.from_user.id

    if data == "set_img":
        btns = InlineKeyboardMarkup([
            [InlineKeyboardButton("Caption", callback_data="cfg_cap"),
             InlineKeyboardButton("Image", callback_data="cfg_img")],
            [InlineKeyboardButton("Button Text", callback_data="cfg_btn")],
            [InlineKeyboardButton("Back", callback_data="back_main")]
        ])
        await callback.message.edit("Image Post Settings", reply_markup=btns)

    elif data == "cfg_cap":
        curr = await get_config("caption")
        await callback.message.reply(f"Current:\n{curr}\n\nSend new caption (Use [link] for link):")
        ans = await client.ask(user_id, "Send Caption:")
        await set_config("caption", ans.text)
        await ans.reply("Updated.")

    elif data == "cfg_img":
        await callback.message.reply("Send new Image URL (or 'delete' to remove):")
        ans = await client.ask(user_id, "URL:")
        if ans.text.lower() == "delete": await set_config("image_url", None)
        else: await set_config("image_url", ans.text)
        await ans.reply("Updated.")

    elif data == "set_time":
        btns = InlineKeyboardMarkup([
            [InlineKeyboardButton("Revoke Time", callback_data="tm_rev"),
             InlineKeyboardButton("Delete Time", callback_data="tm_del")],
            [InlineKeyboardButton("Back", callback_data="back_main")]
        ])
        await callback.message.edit("Timer Settings", reply_markup=btns)
        
    elif data == "tm_rev":
        await callback.message.reply("Send Revoke Time (e.g. 1h, 30m):")
        ans = await client.ask(user_id, "Time:")
        sec = get_seconds(ans.text)
        await set_config("revoke_time", sec)
        await ans.reply(f"Set to {sec}s")

    elif data == "set_fsub":
        state = await get_config("fsub_on", False)
        lbl = "Turn OFF" if state else "Turn ON"
        btns = InlineKeyboardMarkup([
            [InlineKeyboardButton(lbl, callback_data="fs_toggle")],
            [InlineKeyboardButton("Channels", callback_data="fs_chans"),
             InlineKeyboardButton("Message", callback_data="fs_msg")],
            [InlineKeyboardButton("Back", callback_data="back_main")]
        ])
        await callback.message.edit(f"Force Sub is {state}", reply_markup=btns)

    elif data == "fs_toggle":
        curr = await get_config("fsub_on", False)
        await set_config("fsub_on", not curr)
        await callback.answer("Toggled")
        await customize_menu(client, callback.message) # refresh

    elif data == "fs_chans":
        chans = await get_fsub_channels()
        txt = "FSub Channels:\n" + "\n".join([str(c['_id']) for c in chans])
        btns = [[InlineKeyboardButton("Add Channel", callback_data="fs_add")],
                [InlineKeyboardButton("Back", callback_data="set_fsub")]]
        await callback.message.edit(txt, reply_markup=InlineKeyboardMarkup(btns))

    elif data == "fs_add":
        await callback.message.reply("Send Channel ID:")
        ans = await client.ask(user_id, "ID:")
        try:
            cid = int(ans.text)
            await add_fsub(cid)
            await ans.reply("Added.")
        except: await ans.reply("Invalid.")

    elif data == "set_maint":
        curr = await get_config("maintenance", False)
        await set_config("maintenance", not curr)
        await callback.answer(f"Maintenance set to {not curr}")
        await callback.message.edit(f"Maintenance Mode: {not curr}")

    elif data == "back_main":
        await customize_menu(client, callback.message)
        
    elif data == "close":
        await callback.message.delete()
