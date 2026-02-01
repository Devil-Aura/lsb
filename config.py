import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    API_ID = int(os.environ.get("APP_ID", "0"))
    API_HASH = os.environ.get("API_HASH", "")
    BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "")
    OWNER_ID = int(os.environ.get("OWNER_ID", "0"))
    DATABASE_URL = os.environ.get("DATABASE_URL", "")
    DATABASE_NAME = os.environ.get("DATABASE_NAME", "linkssharing")
    LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", "0"))  # For logs if needed
    
    # Customization Defaults
    START_PIC = os.environ.get("START_PIC", "https://telegra.ph/file/f3d3aff9ec422158feb05-d2180e3665e0ac4d32.jpg")
    
    # Admins
    ADMINS = [int(x) for x in os.environ.get("ADMINS", "").split()] if os.environ.get("ADMINS") else []
    if OWNER_ID not in ADMINS:
        ADMINS.append(OWNER_ID)

