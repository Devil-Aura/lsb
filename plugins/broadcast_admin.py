import asyncio
import json
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait, InputUserDeactivated, UserIsBlocked
from config import OWNER_ID
from database.database import get_all_users, total_users_count, get_all_channels, add_admin, remove_admin, is_admin, get_admins

# --- Broadcast Logic ---
@Client.on_message(filters.command(["broadcast", "pbroadcast", "dbroadcast"]) & filters.private)
async def broadcast_handler(client, message):
    if not await is_admin(message.from_user.id) and message.from_user.id != OWNER_ID: return
    if not message.reply_to_message: return await message.reply("Reply to a message.")

    mode = message.command[0]
    pin = True if mode == "pbroadcast" else False
    delete_after = 0
    
    # Handle /dbroadcast 1h
    if mode == "dbroadcast":
        try: delete_after = get_seconds(message.command[1])
        except: return await message.reply("Usage: /dbroadcast 1h")

    users = await get_all_users()
    msg = await message.reply(f"Broadcasting to {len(users)} users...")
    
    done, blocked, deleted, error = 0, 0, 0, 0
    
    for user_id in users:
        try:
            sent = await message.reply_to_message.copy(user_id)
            if pin:
                try: await sent.pin(disable_notification=False)
                except: pass
            if delete_after > 0:
                asyncio.create_task(delete_later(sent, delete_after))
            done += 1
        except FloodWait as e:
            await asyncio.sleep(e.value)
            # Retry once
            try: await message.reply_to_message.copy(user_id)
            except: pass
        except UserIsBlocked: blocked += 1
        except InputUserDeactivated: deleted += 1
        except: error += 1
        
    await msg.edit(f"Completed.\nSuccess: {done}\nBlocked: {blocked}\nDeleted: {deleted}")

async def delete_later(msg, delay):
    await asyncio.sleep(delay)
    try: await msg.delete()
    except: pass

# --- Admin System ---
@Client.on_message(filters.command("admins") & filters.user(OWNER_ID))
async def list_admins_cmd(client, message):
    admins = await get_admins()
    btns = []
    for uid in admins:
        try:
            u = await client.get_users(uid)
            label = u.first_name
        except: label = f"User {uid}"
        btns.append([InlineKeyboardButton(label, callback_data=f"adm_vw_{uid}")])
    
    btns.append([InlineKeyboardButton("➕ Add Admin", callback_data="adm_add")])
    await message.reply("Admins:", reply_markup=InlineKeyboardMarkup(btns))

@Client.on_callback_query(filters.regex("^adm_add"))
async def add_admin_cb(client, callback):
    try:
        ask = await client.ask(callback.from_user.id, "Send Admin User ID:", timeout=30)
        uid = int(ask.text)
        await add_admin(uid)
        await ask.reply(f"Added {uid}")
    except:
        await callback.message.reply("Cancelled.")

@Client.on_callback_query(filters.regex("^adm_vw_"))
async def view_admin_cb(client, callback):
    uid = int(callback.data.split("_")[2])
    btns = [[InlineKeyboardButton("Remove Admin", callback_data=f"adm_rem_{uid}")],
            [InlineKeyboardButton("Back", callback_data="adm_back")]]
    await callback.message.edit(f"Admin ID: {uid}", reply_markup=InlineKeyboardMarkup(btns))

@Client.on_callback_query(filters.regex("^adm_rem_"))
async def rem_admin_cb(client, callback):
    uid = int(callback.data.split("_")[2])
    await remove_admin(uid)
    await callback.message.edit("Admin Removed.")

# --- Backup ---
@Client.on_message(filters.command("backup") & filters.user(OWNER_ID))
async def backup_cmd(client, message):
    # Dumps channel list to JSON file
    channels = await get_all_channels()
    with open("backup_channels.json", "w") as f:
        json.dump(channels, f, indent=4, default=str)
    await message.reply_document("backup_channels.json")
