import asyncio
import logging
from pyrogram import Client
from aiohttp import web
from config import API_ID, API_HASH, BOT_TOKEN, OWNER_ID, PORT
from database.database import add_admin, init_defaults
import pyromod # Important for user input

logging.basicConfig(level=logging.INFO)

class Bot(Client):
    def __init__(self):
        super().__init__(
            "CrunchyBot",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            plugins=dict(root="plugins")
        )

    async def start(self):
        await super().start()
        me = await self.get_me()
        self.username = me.username
        self.uptime = asyncio.get_running_loop().time()
        
        # Init Database Defaults
        await add_admin(OWNER_ID)
        await init_defaults()
        
        print(f"Bot Started as {me.username}")
        try:
            await self.send_message(OWNER_ID, "<b>🤖 Bot Started Successfully!</b>")
        except:
            pass

        # Web Server for Uptime
        app = web.Application()
        app.router.add_get("/", lambda r: web.Response(text="Bot Running"))
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", PORT)
        await site.start()

    async def stop(self, *args):
        await super().stop()

if __name__ == "__main__":
    Bot().run()
