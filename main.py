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
from threading import Thread
from flask import Flask

# Initialize Flask app for health check
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "Bot is running!", 200

@web_app.route('/health')
def health():
    return "OK", 200

def run_flask():
    """Run Flask server in a separate thread"""
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

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
    
    # Start Flask server in a separate thread
    print("🌐 Starting health check server...")
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # Run the bot
    app.run()
