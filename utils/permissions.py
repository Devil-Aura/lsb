from database.mongo import admins
from config import OWNER_ID

async def is_owner(user_id: int):
    return user_id == OWNER_ID

async def is_admin(user_id: int):
    if user_id == OWNER_ID:
        return True
    return await admins.find_one({"user_id": user_id}) is not None
