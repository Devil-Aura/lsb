from pyrogram import Client, idle
from config import Config
from database import db
import logging
import asyncio

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s - %(levelname)s] - %(name)s - %(message)s",
    datefmt='%d-%b-%y %H:%M:%S',
)
logger = logging.getLogger(__name__)

class Bot(Client):
    def __init__(self):
        super().__init__(
            name="LinkShareBot",
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.BOT_TOKEN,
            plugins=dict(root="plugins"),
            workers=50,
            sleep_threshold=10,
        )

    async def start(self):
        await super().start()
        me = await self.get_me()
        logger.info(f"Bot Started as @{me.username}")
        
        # Notify Owner
        try:
            if Config.OWNER_ID:
                await self.send_message(Config.OWNER_ID, "<b>🤖 Bot Restarted ♻️</b>")
        except Exception as e:
            logger.warning(f"Could not notify owner: {e}")

    async def stop(self, *args):
        await super().stop()
        logger.info("Bot Stopped")

if __name__ == "__main__":
    # Ensure event loop
    loop = asyncio.get_event_loop_policy().get_event_loop()
    loop.run_until_complete(Bot().run())
