import os
import asyncio
import datetime
import pytz
import requests
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ForceReply, InputMediaPhoto
from config import Config
from database import db
from script import script
from utils import get_size

# Initialize bot
app = Client(
    "RenameBot",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN,
    plugins=dict(root="plugins")
)

if __name__ == "__main__":
    print("🤖 Rename Bot Starting...")
    print(f"📊 Free User Limit: {Config.FREE_USER_LIMIT / (1024**3):.1f}GB")
    print(f"💎 Premium User Limit: {Config.PREMIUM_USER_LIMIT / (1024**3):.1f}GB")
    app.run()
