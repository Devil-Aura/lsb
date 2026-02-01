import motor.motor_asyncio
from config import DATABASE_URL, DATABASE_NAME
from datetime import datetime

client = motor.motor_asyncio.AsyncIOMotorClient(DATABASE_URL)
db = client[DATABASE_NAME]

# Collections
users_col = db['users']
channels_col = db['channels']
settings_col = db['settings']
admins_col = db['admins']
fsub_col = db['fsub_channels']

# --- User ---
async def add_user(user_id, name):
    await users_col.update_one({'_id': user_id}, {'$set': {'name': name}}, upsert=True)

async def get_all_users():
    return [doc['_id'] async for doc in users_col.find()]

async def total_users_count():
    return await users_col.count_documents({})

# --- Admin ---
async def add_admin(user_id):
    await admins_col.update_one({'_id': user_id}, {'$set': {'role': 'admin'}}, upsert=True)

async def remove_admin(user_id):
    await admins_col.delete_one({'_id': user_id})

async def is_admin(user_id):
    return await admins_col.find_one({'_id': user_id})

async def get_admins():
    return [doc['_id'] async for doc in admins_col.find()]

# --- Channel ---
async def add_channel(channel_id, anime_name, primary_link):
    await channels_col.update_one(
        {'_id': channel_id},
        {'$set': {'name': anime_name, 'primary_link': primary_link}},
        upsert=True
    )

async def delete_channel(channel_id):
    await channels_col.delete_one({'_id': channel_id})

async def get_channel(channel_id):
    return await channels_col.find_one({'_id': channel_id})

async def get_all_channels():
    return await channels_col.find().to_list(length=None)

async def search_channel(query):
    return await channels_col.find({"name": {"$regex": query, "$options": "i"}}).to_list(length=None)

# --- Settings ---
async def set_config(key, value):
    await settings_col.update_one({'_id': 'main_config'}, {'$set': {key: value}}, upsert=True)

async def get_config(key, default=None):
    data = await settings_col.find_one({'_id': 'main_config'})
    if data and key in data:
        return data[key]
    return default

# --- Force Sub ---
async def add_fsub(channel_id, req_mode=False):
    await fsub_col.update_one({'_id': channel_id}, {'$set': {'req_mode': req_mode}}, upsert=True)

async def get_fsub_channels():
    return await fsub_col.find().to_list(length=None)

async def del_fsub(channel_id):
    await fsub_col.delete_one({'_id': channel_id})

# Defaults
async def init_defaults():
    if not await get_config("caption"):
        await set_config("caption", "Please Join The Channel By Clicking The Link Or Button\nLink: [link]")
    if not await get_config("btn_text"):
        await set_config("btn_text", "⛩️ 𝗖𝗟𝗜𝗖𝗞 𝗛𝗘𝗥𝗘 𝗧𝗢 𝗝𝗢𝗜𝗇 ⛩️")
    if not await get_config("revoke_time"):
        await set_config("revoke_time", 1800) # 30 mins
    if not await get_config("delete_time"):
        await set_config("delete_time", 1800)
    if not await get_config("fsub_msg"):
        await set_config("fsub_msg", "<b>ʀᴏᴋᴏ {first}!</b>\n\n<b>ᴛᴜᴍɴᴇ ᴀʙʜɪ ᴛᴀᴋ ʜᴀᴍᴀʀᴀ ᴀɴɪᴍᴇ ᴄʜᴀɴɴᴇʟ ᴊᴏɪɴ ɴᴀʜɪɴ ᴋɪʏᴀ ʜᴀɪ!</b>")
