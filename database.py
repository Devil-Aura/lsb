import motor.motor_asyncio
from config import Config
from datetime import datetime

class Database:
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.users = self.db.users
        self.channels = self.db.channels
        self.settings = self.db.settings
        self.admins = self.db.admins

    # User Methods
    async def add_user(self, user_id, name):
        if not await self.users.find_one({"_id": user_id}):
            await self.users.insert_one({"_id": user_id, "name": name, "joined_date": datetime.now()})

    async def get_all_users(self):
        return [user async for user in self.users.find({})]

    async def get_total_users(self):
        return await self.users.count_documents({})

    # Channel Methods
    async def add_channel(self, anime_name, channel_id, primary_link):
        await self.channels.update_one(
            {"channel_id": channel_id},
            {"$set": {"anime_name": anime_name, "primary_link": primary_link, "channel_id": channel_id}},
            upsert=True
        )

    async def get_channel(self, channel_id):
        return await self.channels.find_one({"channel_id": channel_id})
    
    async def get_channel_by_name(self, anime_name):
        # Case insensitive search
        return await self.channels.find_one({"anime_name": {"$regex": f"^{anime_name}$", "$options": "i"}})

    async def search_channels(self, query):
        return [channel async for channel in self.channels.find({"anime_name": {"$regex": query, "$options": "i"}})]

    async def get_all_channels(self):
        return [channel async for channel in self.channels.find({})]

    async def delete_channel(self, channel_id):
        await self.channels.delete_one({"channel_id": channel_id})

    async def get_total_channels(self):
        return await self.channels.count_documents({})

    # Admin Methods
    async def add_admin(self, user_id):
        if not await self.admins.find_one({"_id": user_id}):
            await self.admins.insert_one({"_id": user_id})
            return True
        return False

    async def remove_admin(self, user_id):
        if await self.admins.find_one({"_id": user_id}):
            await self.admins.delete_one({"_id": user_id})
            return True
        return False

    async def get_admins(self):
        return [admin["_id"] async for admin in self.admins.find({})]

    async def is_admin(self, user_id):
        if user_id == Config.OWNER_ID:
            return True
        if user_id in Config.ADMINS:
            return True
        return bool(await self.admins.find_one({"_id": user_id}))

    # Customization Methods
    async def update_setting(self, key, value):
        await self.settings.update_one(
            {"_id": "main_settings"},
            {"$set": {key: value}},
            upsert=True
        )

    async def get_setting(self, key, default=None):
        doc = await self.settings.find_one({"_id": "main_settings"})
        return doc.get(key, default) if doc else default

db = Database(Config.DATABASE_URL, Config.DATABASE_NAME)
