from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN

app = Client(
    "CrunchyrollLinkBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

import handlers.public
import handlers.admin
import handlers.channels
import handlers.broadcast
import handlers.force_sub
import handlers.customize
import handlers.stats

if __name__ == "__main__":
    print("Bot Started...")
    app.run()
