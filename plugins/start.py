import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from config import Config
from database import db
from helper_func import decode, get_readable_time
from datetime import datetime

# We will import handle_deep_link inside the function to avoid circular imports if necessary
# or just ensure channels.py is loaded. 

@Client.on_message(filters.command("start") & filters.private)
async def start_command(client: Client, message: Message):
    if len(message.command) > 1:
        # Deep linking
        payload = message.command[1]
        from plugins.channels import handle_deep_link
        await handle_deep_link(client, message, payload)
        return

    # Normal Start
    start_text = """
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
    
    # Send Start Message
    msg = await message.reply_text(
        text=start_text,
        disable_web_page_preview=True
    )
    
    # Auto Delete after 15 minutes (900 seconds)
    await asyncio.sleep(900)
    try:
        await msg.delete()
        await message.delete()
    except:
        pass

@Client.on_message(filters.command("help") & filters.private)
async def help_command(client: Client, message: Message):
    help_text = """<blockquote expandable>
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
</blockquote>"""

    msg = await message.reply_text(help_text, disable_web_page_preview=True)
    
    # Auto delete after 2 minutes (120 seconds)
    await asyncio.sleep(120)
    try:
        await msg.delete()
        await message.delete()
    except:
        pass

@Client.on_message(filters.command(["about", "info"]) & filters.private)
async def about_command(client: Client, message: Message):
    # Calculate Age
    start_date = datetime(2026, 1, 26)
    now = datetime.now()
    age_days = (now - start_date).days
    
    about_text = f"""
About The Bot 
🤖 My Name :- <a href='https://telegra.ph/Crunchy-Roll-Vault-04-08'>Crunchyroll Link Provider</a>\n
Bot Age :- {age_days} Day(s) (26/01/2026)
Anime Channel :- <a href='https://t.me/Crunchyrollchannel'>Crunchy Roll Channel</a>
Language :- <a href='https://t.me/Crunchyrollchannel'>Python</a>
Developer: :- <a href='https://t.me/World_Fastest_Bots'>World Fastest Bots</a>

This Is Private/Paid Bot Provided By 
@World_Fastest_Bots.
    """
    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("📡 𝗣𝗼𝘄𝗲𝗿𝗲𝗱 𝗕𝘆", url="https://t.me/World_Fastest_Bots")],
        [InlineKeyboardButton("World Fastest Bots", url="https://t.me/World_Fastest_Bots")]
    ])
    
    msg = await message.reply_text(about_text, reply_markup=buttons, disable_web_page_preview=True)
    
    # Auto delete after 1 minute (60 seconds)
    await asyncio.sleep(60)
    try:
        await msg.delete()
        await message.delete()
    except:
        pass
