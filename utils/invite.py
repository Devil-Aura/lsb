from datetime import datetime, timedelta
from database.mongo import invites
from utils.scheduler import revoke_invite_after_delay
import asyncio

async def get_or_create_invite(app, channel_id, request_mode, revoke_time):

    existing = await invites.find_one({"channel_id": channel_id})

    if existing:
        remaining = (
            existing["expire_time"] - datetime.utcnow()
        ).total_seconds()

        if remaining > 60:
            return existing["invite_link"]

    if request_mode:
        invite = await app.create_chat_invite_link(
            channel_id,
            creates_join_request=True,
            expire_date=datetime.utcnow() + timedelta(seconds=revoke_time)
        )
    else:
        invite = await app.create_chat_invite_link(
            channel_id,
            expire_date=datetime.utcnow() + timedelta(seconds=revoke_time)
        )

    invite_link = invite.invite_link

    await invites.update_one(
        {"channel_id": channel_id},
        {"$set": {
            "invite_link": invite_link,
            "expire_time": datetime.utcnow() + timedelta(seconds=revoke_time)
        }},
        upsert=True
    )

    asyncio.create_task(
        revoke_invite_after_delay(app, channel_id, invite_link, revoke_time)
    )

    return invite_link
