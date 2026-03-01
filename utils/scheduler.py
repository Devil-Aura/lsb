import asyncio

async def delete_after_delay(app, chat_id, message_ids, delay):
    await asyncio.sleep(delay)
    for msg_id in message_ids:
        try:
            await app.delete_messages(chat_id, msg_id)
        except:
            pass

async def revoke_invite_after_delay(app, channel_id, invite_link, delay):
    await asyncio.sleep(delay)
    try:
        await app.revoke_chat_invite_link(channel_id, invite_link)
    except:
        pass
