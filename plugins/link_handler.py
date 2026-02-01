import asyncio
from datetime import datetime, timedelta
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.database import get_channel, get_config, get_fsub_channels, is_admin
from helper_func import decode, get_seconds, get_readable_time

async def handle_deep_link(client, message, token):
    try:
        decoded = await decode(token)
        # Format: mode_channelID_random
        # Modes: req, norm, ext
        parts = decoded.split("_")
        mode = parts[0]
        
        # --- FORCE SUB CHECK ---
        user_id = message.from_user.id
        fsub_status = await get_config("fsub_on", False)
        if fsub_status and not await is_admin(user_id):
            fchannels = await get_fsub_channels()
            not_joined = []
            for ch in fchannels:
                try:
                    await client.get_chat_member(ch['_id'], user_id)
                except:
                    # User not in channel
                    # Generate temporary invite
                    try:
                        invite = await client.create_chat_invite_link(ch['_id'], member_limit=1, expire_date=datetime.now()+timedelta(minutes=5))
                        link = invite.invite_link
                    except:
                        link = "https://t.me/" # Fallback
                    not_joined.append([InlineKeyboardButton("Join Channel", url=link)])
            
            if not_joined:
                fsub_msg = await get_config("fsub_msg")
                fsub_msg = fsub_msg.format(first=message.from_user.first_name)
                not_joined.append([InlineKeyboardButton("Try Again", url=f"https://t.me/{client.username}?start={token}")])
                return await message.reply(fsub_msg, reply_markup=InlineKeyboardMarkup(not_joined))

        # --- PROCESS LINK ---
        if mode == "ext":
            # External URL logic
            url = parts[1] # For simplicity in encoding
            # In real scenario, URL is likely stored in DB and ID is passed here to keep token short
            await message.reply(f"🔗 External Link:\n{url}")
            return

        channel_id = int(parts[1])
        channel_data = await get_channel(channel_id)
        
        if not channel_data:
            return await message.reply("Link Expired or Channel Removed.")

        # Settings
        img_url = await get_config("image_url", "https://telegra.ph/Crunchy-Roll-Vault-04-08")
        caption_tpl = await get_config("caption")
        btn_txt = await get_config("btn_text")
        revoke_sec = await get_config("revoke_time", 1800)
        delete_sec = await get_config("delete_time", 1800)
        sec_msg_on = await get_config("sec_msg_on", True)
        sec_msg_txt = await get_config("sec_msg_text", "Please Join The Channel... Link Expires in few mins.")

        # Generate Link
        is_req = True if mode == "req" else False
        invite = await client.create_chat_invite_link(
            chat_id=channel_id,
            name=f"User_{message.from_user.id}",
            creates_join_request=is_req,
            expire_date=datetime.now() + timedelta(seconds=revoke_sec)
        )
        
        link = invite.invite_link
        final_caption = caption_tpl.replace("[link]", link)
        
        btn = InlineKeyboardMarkup([[InlineKeyboardButton(btn_txt, url=link)]])
        
        # Send Messages
        if img_url and img_url.startswith("http"):
            msg1 = await message.reply_photo(img_url, caption=final_caption, reply_markup=btn)
        else:
            msg1 = await message.reply(final_caption, reply_markup=btn) # Fallback if no image

        to_delete = [msg1.id]

        if sec_msg_on:
            msg2 = await msg1.reply(sec_msg_txt, quote=True)
            to_delete.append(msg2.id)

        # Schedule Delete
        asyncio.create_task(auto_delete(client, message.chat.id, to_delete, delete_sec))

    except Exception as e:
        print(f"Error: {e}")
        await message.reply("Invalid Link.")

async def auto_delete(client, chat_id, msg_ids, delay):
    await asyncio.sleep(delay)
    try: await client.delete_messages(chat_id, msg_ids)
    except: pass
