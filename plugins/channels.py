import asyncio
import time
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import FloodWait, ChatAdminRequired
from config import Config
from database import db
from helper_func import encode, decode, is_owner_or_admin, get_readable_time

# --- /addchannel ---
@Client.on_message(filters.command("addchannel") & is_owner_or_admin)
async def add_channel(client: Client, message: Message):
    if len(message.command) < 3:
        return await message.reply_text("Usage: /addchannel [Anime Name] [Channel ID]")
    
    anime_name = " ".join(message.command[1:-1])
    try:
        channel_id = int(message.command[-1])
    except ValueError:
        return await message.reply_text("Invalid Channel ID")
        
    # Check if bot is admin in channel
    try:
        member = await client.get_chat_member(channel_id, client.me.id)
        if not member.privileges.can_invite_users:
            return await message.reply_text("I don't have 'Invite Users' permission in that channel.")
    except Exception as e:
        return await message.reply_text(f"Error: {e}\nMake sure I am added to the channel as Admin.")

    # Generate Primary Link (Permanent)
    try:
        primary_link = await client.create_chat_invite_link(channel_id, name="Primary Link")
        primary_link = primary_link.invite_link
    except Exception as e:
        return await message.reply_text(f"Failed to create Primary Link: {e}")

    await db.add_channel(anime_name, channel_id, primary_link)
    await message.reply_text(f"Successfully Added Channel **{anime_name}**\nPrimary Link: {primary_link}")

# --- /channels ---
@Client.on_message(filters.command("channels") & is_owner_or_admin)
async def list_channels(client: Client, message: Message):
    channels = await db.get_all_channels()
    if not channels:
        return await message.reply_text("No channels added.")
    
    text = "<b>List of Channels:</b>\n\n"
    for i, channel in enumerate(channels, 1):
        c_id = channel['channel_id']
        name = channel['anime_name']
        p_link = channel.get('primary_link', 'N/A')
        
        # Generate deep links
        # We encode channel_id to keep it short and somewhat opaque
        req_payload = f"req_{c_id}"
        norm_payload = f"norm_{c_id}"
        
        req_payload_enc = await encode(req_payload)
        norm_payload_enc = await encode(norm_payload)
        
        bot_username = client.me.username
        req_link = f"https://t.me/{bot_username}?start={req_payload_enc}"
        norm_link = f"https://t.me/{bot_username}?start={norm_payload_enc}"
        
        text += f"{i}. <b>{name}</b>\nPrimary: {p_link}\nRequest: {req_link}\nNormal: {norm_link}\n\n"
    
    # In a real scenario, we would paginate 'text' if it's too long.
    # For now, splitting if > 4096 chars
    if len(text) > 4096:
        # Simple chunking
        for x in range(0, len(text), 4096):
            await message.reply_text(text[x:x+4096], disable_web_page_preview=True)
    else:
        await message.reply_text(text, disable_web_page_preview=True)

# --- /delchannel ---
@Client.on_message(filters.command("delchannel") & is_owner_or_admin)
async def delete_channel(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: /delchannel [Channel ID]")
    
    try:
        channel_id = int(message.command[1])
        await db.delete_channel(channel_id)
        await message.reply_text(f"Deleted channel {channel_id} from database.")
    except ValueError:
        await message.reply_text("Invalid ID.")

# --- /search ---
@Client.on_message(filters.command("search"))
async def search_channel(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: /search [Anime Name]")
    
    query = " ".join(message.command[1:])
    results = await db.search_channels(query)
    
    if not results:
        return await message.reply_text("No results found.")
    
    buttons = []
    for channel in results:
        name = channel['anime_name']
        c_id = channel['channel_id']
        buttons.append([InlineKeyboardButton(name, callback_data=f"view_ch_{c_id}")])
        
    await message.reply_text(f"Search Results for '{query}':", reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_callback_query(filters.regex(r"^view_ch_"))
async def view_channel_callback(client: Client, callback_query: CallbackQuery):
    c_id = int(callback_query.data.split("_")[2])
    channel = await db.get_channel(c_id)
    if not channel:
        return await callback_query.answer("Channel not found.", show_alert=True)
    
    name = channel['anime_name']
    p_link = channel.get('primary_link', 'N/A')
    
    req_payload = f"req_{c_id}"
    norm_payload = f"norm_{c_id}"
    req_payload_enc = await encode(req_payload)
    norm_payload_enc = await encode(norm_payload)
    
    bot_username = client.me.username
    req_link = f"https://t.me/{bot_username}?start={req_payload_enc}"
    norm_link = f"https://t.me/{bot_username}?start={norm_payload_enc}"
    
    text = f"<b>{name}</b>\n\nPrimary: {p_link}\nRequest: {req_link}\nNormal: {norm_link}"
    
    await callback_query.message.edit_text(text, disable_web_page_preview=True)

# --- Deep Link Handler ---
async def handle_deep_link(client: Client, message: Message, payload: str):
    try:
        decoded_payload = await decode(payload)
    except:
        return await message.reply_text("Invalid Link.")
    
    prefix, channel_id_str = decoded_payload.split("_", 1)
    try:
        channel_id = int(channel_id_str)
    except:
        return await message.reply_text("Invalid Channel ID in link.")
    
    channel = await db.get_channel(channel_id)
    if not channel:
        return await message.reply_text("Channel not found in database.")
    
    # Generate Temporary Invite Link
    # Logic: 
    # 1. Create invite link (expire in 30 mins)
    # 2. If req_, creates_join_request=True
    # 3. If norm_, creates_join_request=False
    
    creates_join_request = (prefix == "req")
    
    try:
        # Create a new link every time or cache? User said: "if the link is expiring after 1 Mintues then don't use the allready link generate new link for it."
        # Simpler to generate new one for robust security unless rate limited.
        # Telegram limit is 50 links per day per admin? No, much higher usually.
        # But to be safe, maybe re-use if valid.
        
        # For simplicity and "Updating code", we will generate fresh links which is cleaner for "Temporary Time".
        invite_link_obj = await client.create_chat_invite_link(
            chat_id=channel_id,
            name=f"Link for {message.from_user.first_name}",
            expire_date=datetime.now().timestamp() + 1800, # 30 mins
            creates_join_request=creates_join_request
        )
        invite_url = invite_link_obj.invite_link
        
    except FloodWait as e:
        return await message.reply_text(f"Please wait {e.value} seconds.")
    except Exception as e:
        return await message.reply_text(f"Error generating link: {e}")
    
    # Send Image + Button
    # Image from Config or Customization
    img_url = await db.get_setting("image_post", Config.START_PIC)
    caption = await db.get_setting("caption", "Channel link 🔗 👇👇")
    button_text = await db.get_setting("button_text", "⛩️ 𝗖𝗟𝗜𝗖𝗞 𝗛𝗘𝗥𝗘 𝗧𝗢 𝗝𝗢𝗜𝗡 ⛩️")
    
    # First Message: Image with Button
    buttons = InlineKeyboardMarkup([[InlineKeyboardButton(button_text, url=invite_url)]])
    
    try:
        msg1 = await message.reply_photo(
            photo=img_url,
            caption=caption,
            reply_markup=buttons
        )
    except Exception as e:
        msg1 = await message.reply_text(
            f"{caption}\n[Image Failed: {e}]",
            reply_markup=buttons
        )

    # Second Message: Reply to Image
    # "Please Join The Channel By Clicking The Link Or Button And This Link Will Expire within few minutes."
    second_msg_text = await db.get_setting("second_msg", "Please Join The Channel By Clicking The Link Or Button And This Link Will Expire within few minutes.")
    
    msg2 = await msg1.reply_text(second_msg_text)
    
    # Auto Delete after 30 mins
    # User said: "this Both Message will delete after 30 Mintues."
    asyncio.create_task(delete_later(msg1, msg2, delay=1800))

async def delete_later(msg1, msg2, delay):
    await asyncio.sleep(delay)
    try:
        await msg1.delete()
        await msg2.delete()
    except:
        pass

from datetime import datetime
