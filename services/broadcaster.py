# services/broadcaster.py

import asyncio
from datetime import datetime, timedelta
from database.mongo import users, broadcast_logs
from utils.scheduler import delete_after_delay


async def broadcast_message(app, message, pin=False, delete_after=None):
    all_users = users.find({})
    success = 0
    failed = 0
    broadcast_ids = []

    async for user in all_users:
        try:
            sent = await message.copy(user["_id"])

            if pin:
                try:
                    await app.pin_chat_message(user["_id"], sent.id)
                except:
                    pass

            if delete_after:
                asyncio.create_task(
                    delete_after_delay(app, user["_id"], [sent.id], delete_after)
                )

            broadcast_ids.append({
                "user_id": user["_id"],
                "message_id": sent.id
            })

            success += 1
        except:
            failed += 1

    await broadcast_logs.insert_one({
        "created_at": datetime.utcnow(),
        "messages": broadcast_ids,
        "pin": pin,
        "delete_after": delete_after
    })

    return success, failed


async def delete_last_broadcast(app):
    last = await broadcast_logs.find_one(sort=[("_id", -1)])
    if not last:
        return False

    for item in last["messages"]:
        try:
            await app.delete_messages(item["user_id"], item["message_id"])
        except:
            pass

    await broadcast_logs.delete_one({"_id": last["_id"]})
    return True


async def delete_all_broadcasts(app):
    async for b in broadcast_logs.find({}):
        for item in b["messages"]:
            try:
                await app.delete_messages(item["user_id"], item["message_id"])
            except:
                pass
    await broadcast_logs.delete_many({})
