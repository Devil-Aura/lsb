import asyncio
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import OWNER_ID
from database.database import is_admin, add_channel, delete_channel, get_all_channels, search_channel, get_channel
from helper_func import encode

@Client.on_message(filters.command("addchannel") & filters.private)
async def add_channel_cmd(client, message):
    user_id = message.from_user.id
    if not await is_admin(user_id) and user_id != OWNER_ID: return

    # /addchannel Name ID
    if len(message.command) < 3:
        return await message.reply("Usage: /addchannel [Anime Name] [Channel ID]")
    
    name = message.command[1]
    try: ch_id = int(message.command[2])
    except: return await message.reply("Invalid ID")

    try:
        # Check permissions
        member = await client.get_chat_member(ch_id, "me")
        if not member.status in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]:
            return await message.reply("I am not admin in that channel.")
        if not member.privileges.can_invite_users:
            return await message.reply("I need 'Invite Users' permission.")
            
        # Primary Link
        link_obj = await client.create_chat_invite_link(ch_id, name="Primary Link", expire_date=None)
        primary_link = link_obj.invite_link
        
        await add_channel(ch_id, name, primary_link)
        await message.reply(f"Successfully Added Channel {name}\nPrimary Link: {primary_link}")
        
    except Exception as e:
        await message.reply(f"Error: {e}")

@Client.on_message(filters.command("channels") & filters.private)
async def list_channels(client, message):
    if not await is_admin(message.from_user.id) and message.from_user.id != OWNER_ID: return

    channels = await get_all_channels()
    if not channels: return await message.reply("No channels found.")
    
    out = ""
    for idx, ch in enumerate(channels, 1):
        try:
            req_token = await encode(f"req_{ch['_id']}_rng")
            norm_token = await encode(f"norm_{ch['_id']}_rng")
            bot_username = client.username
            
            out += f"{idx}. {ch['name']} (<a href='{ch['primary_link']}'>Primary</a>)\n"
            out += f"[Request Link](https://t.me/{bot_username}?start={req_token}) | "
            out += f"[Normal Link](https://t.me/{bot_username}?start={norm_token})\n\n"
        except: pass
        
        if len(out) > 3500: # Split large messages
            await message.reply(out, disable_web_page_preview=True)
            out = ""
            
    if out: await message.reply(out, disable_web_page_preview=True)

@Client.on_message(filters.command("search") & filters.private)
async def search_cmd(client, message):
    if len(message.command) < 2: return await message.reply("Usage: /search [Name]")
    query = message.text.split(" ", 1)[1]
    results = await search_channel(query)
    
    if not results: return await message.reply("No results.")
    
    btns = []
    for r in results:
        btns.append([InlineKeyboardButton(r['name'], callback_data=f"show_ch_{r['_id']}")])
        
    await message.reply("Here Are Some Search Results 🔎", reply_markup=InlineKeyboardMarkup(btns))

@Client.on_callback_query(filters.regex("^show_ch_"))
async def show_ch_details(client, callback):
    ch_id = int(callback.data.split("_")[2])
    ch = await get_channel(ch_id)
    if not ch: return await callback.answer("Channel not found", show_alert=True)
    
    req_token = await encode(f"req_{ch['_id']}_rng")
    norm_token = await encode(f"norm_{ch['_id']}_rng")
    bot_u = client.username
    
    txt = f"<b>{ch['name']}</b>\nPrimary: {ch['primary_link']}\n\n"
    txt += f"Request: https://t.me/{bot_u}?start={req_token}\n"
    txt += f"Normal: https://t.me/{bot_u}?start={norm_token}"
    
    await callback.message.edit(txt, disable_web_page_preview=True)

@Client.on_message(filters.command("delchannel") & filters.private)
async def del_ch(client, message):
    if not await is_admin(message.from_user.id) and message.from_user.id != OWNER_ID: return
    try:
        cid = int(message.command[1])
        await delete_channel(cid)
        await message.reply("Channel Removed.")
    except:
        await message.reply("Usage: /delchannel [ID]")

@Client.on_message(filters.command("genlink") & filters.private)
async def genlink(client, message):
    # Generates a link for External URL
    if not await is_admin(message.from_user.id) and message.from_user.id != OWNER_ID: return
    if len(message.command) < 2: return await message.reply("/genlink [URL]")
    
    url = message.text.split(" ", 1)[1]
    # In a full production bot, you'd save URL to DB and use ID.
    # Here we embed for demonstration (Note: URL length limits in deep link)
    token = await encode(f"ext_{url}") 
    link = f"https://t.me/{client.username}?start={token}"
    
    await message.reply(f"Generated Link:\n{link}\n\n(Note: This link does not expire, but the message sent by bot will delete after 30 mins)")
