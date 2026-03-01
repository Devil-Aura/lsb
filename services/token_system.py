# services/token_system.py

import secrets
from datetime import datetime, timedelta
from database.mongo import tokens

TOKEN_EXPIRY_MINUTES = 10

async def generate_token(user_id):
    token = secrets.token_urlsafe(16)

    await tokens.insert_one({
        "token": token,
        "user_id": user_id,
        "expires_at": datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRY_MINUTES)
    })

    return token

async def verify_token(token):
    data = await tokens.find_one({"token": token})
    if not data:
        return False

    if datetime.utcnow() > data["expires_at"]:
        await tokens.delete_one({"token": token})
        return False

    await tokens.delete_one({"token": token})
    return True
