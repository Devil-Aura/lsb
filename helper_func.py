import base64
import asyncio
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Base64 Encoding/Decoding for Deep Links
async def encode(string):
    string_bytes = str(string).encode("ascii")
    base64_bytes = base64.urlsafe_b64encode(string_bytes)
    return base64_bytes.decode("ascii").strip("=")

async def decode(base64_string):
    base64_string = base64_string.strip("=")
    base64_bytes = (base64_string + "=" * (-len(base64_string) % 4)).encode("ascii")
    string_bytes = base64.urlsafe_b64decode(base64_bytes)
    return string_bytes.decode("ascii")

# Time Parser (1H, 30M, 30s) -> Seconds
def get_seconds(time_string):
    try:
        unit = time_string[-1].lower()
        value = int(time_string[:-1])
        if unit == 's': return value
        elif unit == 'm': return value * 60
        elif unit == 'h': return value * 3600
        elif unit == 'd': return value * 86400
        return 0
    except:
        return 0

# Readable Time (Seconds -> "1h 30m 10s")
def get_readable_time(seconds):
    result = ""
    (days, remainder) = divmod(seconds, 86400)
    if days > 0: result += f"{int(days)}d "
    (hours, remainder) = divmod(remainder, 3600)
    if hours > 0: result += f"{int(hours)}h "
    (minutes, seconds) = divmod(remainder, 60)
    if minutes > 0: result += f"{int(minutes)}m "
    result += f"{int(seconds)}s"
    return result.strip()
