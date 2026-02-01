import os

# Credentials from your description
API_ID = int(os.environ.get("API_ID", "22768311"))
API_HASH = os.environ.get("API_HASH", "702d8884f48b42e865425391432b3794")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "") # Enter your Bot Token here or in ENV
OWNER_ID = int(os.environ.get("OWNER_ID", "6040503076"))
DATABASE_URL = os.environ.get("DATABASE_URL", "mongodb+srv://link:link0123@cluster0.wm6zb7x.mongodb.net/?appName=Cluster0")
DATABASE_NAME = "CrunchyRollVault"

# Web Port
PORT = int(os.environ.get("PORT", 8080))
