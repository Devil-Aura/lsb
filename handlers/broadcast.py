# handlers/broadcast.py

import asyncio
from pyrogram import filters
from bot import app
from utils.permissions import is_admin
from services.broadcaster import (
    broadcast_message,
    delete_last_broadcast,
    delete_all_broadcasts
)

batch_buffer = {}


# ================= NORMAL BROADCAST =================

@app.on_message(filters.command("broadcast") & filters.reply)
async def broadcast_handler(client, message):
    if not await is_admin(message.from_user.id):
        return

    status = await message.reply("Broadcasting...")

    success, failed = await broadcast_message(
        app,
        message.reply_to_message
    )

    await status.edit(
        f"Broadcast Complete\nSuccess: {success}\nFailed: {failed}"
    )


# ================= PIN BROADCAST =================

@app.on_message(filters.command("pbroadcast") & filters.reply)
async def pbroadcast_handler(client, message):
    if not await is_admin(message.from_user.id):
        return

    success, failed = await broadcast_message(
        app,
        message.reply_to_message,
        pin=True
    )

    await message.reply(
        f"Pinned Broadcast Complete\nSuccess: {success}\nFailed: {failed}"
    )


# ================= TEMP BROADCAST =================

@app.on_message(filters.command("dbroadcast") & filters.reply)
async def dbroadcast_handler(client, message):
    if not await is_admin(message.from_user.id):
        return

    args = message.command[1:]
    seconds = parse_time(args)

    success, failed = await broadcast_message(
        app,
        message.reply_to_message,
        delete_after=seconds
    )

    await message.reply(
        f"Temporary Broadcast Sent\nDeletes in {seconds}s\nSuccess: {success}"
    )


def parse_time(args):
    total = 0
    for arg in args:
        if arg.endswith("D"):
            total += int(arg[:-1]) * 86400
        elif arg.endswith("H"):
            total += int(arg[:-1]) * 3600
        elif arg.endswith("M"):
            total += int(arg[:-1]) * 60
        elif arg.endswith("S"):
            total += int(arg[:-1])
    return total


# ================= DELETE LAST =================

@app.on_message(filters.command("delbroadcast"))
async def del_last(client, message):
    if not await is_admin(message.from_user.id):
        return

    ok = await delete_last_broadcast(app)
    await message.reply("Last Broadcast Deleted." if ok else "No Broadcast Found.")


@app.on_message(filters.command("delallbroadcast"))
async def del_all(client, message):
    if not await is_admin(message.from_user.id):
        return

    await delete_all_broadcasts(app)
    await message.reply("All Broadcasts Deleted.")


# ================= BATCH BROADCAST =================

@app.on_message(filters.command("batchbroadcast"))
async def batch_start(client, message):
    if not await is_admin(message.from_user.id):
        return

    batch_buffer[message.from_user.id] = []
    await message.reply("Send all messages then send /done")


@app.on_message(filters.command("done"))
async def batch_done(client, message):
    if message.from_user.id not in batch_buffer:
        return

    messages = batch_buffer.pop(message.from_user.id)

    for msg in messages:
        await broadcast_message(app, msg)

    await message.reply("Batch Broadcast Completed.")


@app.on_message(filters.private & ~filters.command(["done", "batchbroadcast"]))
async def collect_batch(client, message):
    if message.from_user.id in batch_buffer:
        batch_buffer[message.from_user.id].append(message)


# ================= CLEAR ALL =================

@app.on_message(filters.command("allbroadcastclear"))
async def clear_all(client, message):
    if not await is_admin(message.from_user.id):
        return

    await delete_all_broadcasts(app)
    await message.reply("All Broadcast Types Cleared.")
