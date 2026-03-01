from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_URL

client = AsyncIOMotorClient(MONGO_URL)
db = client["CrunchyrollLinkBot"]

users = db["users"]
admins = db["admins"]
channels = db["channels"]
invites = db["invites"]
settings = db["settings"]
force_sub = db["force_sub"]
broadcast_logs = db["broadcast_logs"]
