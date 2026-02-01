import asyncio
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import OWNER_ID
from database.database import add_user, get_config, total_users_count, get_all_channels, get_fsub_channels, is_admin
from helper_func import decode, get_readable_time, get_seconds

# --- Messages ---
START_TXT = """
Konnichiwa! 🤗
Mera Naam **Crunchyroll Link Provider** hai.  

Main aapko **anime channels** ki links provide karta hu, Iss Anime Ke Channel Se.

<blockquote>
🔹 Agar aapko kisi anime ki link chahiye,<br>
🔹 Ya channel ki link nahi mil rahi hai,<br>
🔹 Ya link expired ho gayi hai
</blockquote>
Toh aap **@CrunchyRollChannel** se New aur working links le sakte hain.  

Shukriya! ❤️
"""

HELP_TXT = """
<blockquote expandable>
 **🆘 Help & Support**  
 Agar aapko kisi bhi help ki zaroorat hai, toh humse yahan sampark karein:  
**@CrunchyRollHelper**
</blockquote>

**🎬 More Anime**  
Agar aap aur anime dekna chahte hain, toh yahan se dekh sakte hain:  
**@CrunchyRollChannel**

<blockquote expandable>
**🤖 Bot Info**  
Bot ki jaankari ke liye /about ya /info ka istemal karein.
</blockquote>
"""

@Client.on_message(filters.command("start") & filters.private)
async def start(client, message):
    user_id = message.from_user.id
    await add_user(user_id, message.from_user.first_name)
    
    # Check Maintenance
    maint_mode = await get_config("maintenance", False)
    if maint_mode and not await is_admin(user_id) and user_id != OWNER_ID:
        return await message.reply("The Bot Is Under Maintenance. Check back later.")

    text = message.text
    if len(text) > 7:
        try:
            token = text.split(" ", 1)[1]
            from plugins.link_handler import handle_deep_link
            await handle_deep_link(client, message, token)
            return
        except Exception as e:
            pass

    msg = await message.reply(START_TXT)
    await asyncio.sleep(900) # 15 mins
    try: await msg.delete() 
    except: pass

@Client.on_message(filters.command("help") & filters.private)
async def help_cmd(client, message):
    msg = await message.reply(HELP_TXT)
    await asyncio.sleep(120) # 2 mins
    try: await msg.delete()
    except: pass

@Client.on_message(filters.command(["about", "info"]) & filters.private)
async def about_cmd(client, message):
    now = datetime.now()
    creation = datetime(2026, 1, 26)
    age = (now - creation).days
    
    txt = f"""
About The Bot 
🤖 My Name :- <a href='https://telegra.ph/Crunchy-Roll-Vault-04-08'>Crunchyroll Link Provider</a>\n
Bot Age :- {age} Days (26/01/2026)
Anime Channel :- <a href='https://t.me/Crunchyrollchannel'>Crunchy Roll Channel</a>
Language :- <a href='https://t.me/Crunchyrollchannel'>Python</a>
Developer: :- <a href='https://t.me/World_Fastest_Bots'>World Fastest Bots</a>

This Is Private/Paid Bot Provided By 
@World_Fastest_Bots.
"""
    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("📡 𝗣𝗼𝘄𝗲𝗿𝗲𝗱 𝗕𝘆", url="https://t.me/World_Fastest_Bots")],
        [InlineKeyboardButton("World Fastest Bots", url="https://t.me/World_Fastest_Bots")]
    ])
    msg = await message.reply(txt, reply_markup=markup, disable_web_page_preview=True)
    await asyncio.sleep(60)
    try: await msg.delete()
    except: pass

@Client.on_message(filters.command("status") & filters.private)
async def status_cmd(client, message):
    if not await is_admin(message.from_user.id) and message.from_user.id != OWNER_ID: return
    uptime = asyncio.get_running_loop().time() - client.uptime
    txt = f"""
⚙️ sʏsᴛᴇᴍ sᴛᴀᴛᴜs

🖥 CPU: 96.3% | RAM: 67.0%
⏱ ᴜᴘᴛɪᴍᴇ: {get_readable_time(uptime)}
🕒 sᴛᴀʀᴛᴇᴅ: 2026-01-23
"""
    await message.reply(txt)

@Client.on_message(filters.command("ping") & filters.private)
async def ping_cmd(client, message):
    start = datetime.now()
    m = await message.reply("Pong!")
    end = datetime.now()
    ms = (end - start).microseconds / 1000
    await m.edit(f"Pong! {ms}ms")
