import os
import asyncio
import datetime
import logging
from pyrogram import Client
from pyrogram.errors import FloodWait
from config import Config
from threading import Thread
from flask import Flask

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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

# Initialize bot with speed optimizations
app = Client(
    Config.SESSION_NAME,
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN,
    
    # Speed Optimizations
    workers=Config.WORKERS,
    workdir=Config.WORKDIR,
    sleep_threshold=Config.SLEEP_THRESHOLD,
    
    plugins=dict(root="plugins")
)

async def start_bot():
    """Start bot with error handling"""
    try:
        await app.start()
        me = await app.get_me()
        
        logger.info(f"✅ Bot started as @{me.username}")
        logger.info(f"⚡ Workers: {Config.WORKERS}")
        logger.info(f"⚡ Sleep Threshold: {Config.SLEEP_THRESHOLD}s")
        logger.info(f"📊 Free User Limit: {Config.FREE_USER_LIMIT / (1024**3):.1f}GB")
        logger.info(f"💎 Premium User Limit: {Config.PREMIUM_USER_LIMIT / (1024**3):.1f}GB")
        
        # Check for tgcrypto
        try:
            import tgcrypto
            logger.info("✅ TgCrypto installed - Maximum speed enabled!")
        except ImportError:
            logger.warning("⚠️ TgCrypto not installed - Install for 10x speed boost!")
            logger.warning("   Run: pip install tgcrypto --break-system-packages")
        
        # Send startup notification to admins
        if Config.ADMINS:
            startup_msg = (
                f"🤖 <b>Bot Started Successfully!</b>\n\n"
                f"<b>Username:</b> @{me.username}\n"
                f"<b>Workers:</b> {Config.WORKERS}\n"
                f"<b>Free Limit:</b> {Config.FREE_USER_LIMIT / (1024**3):.1f}GB\n"
                f"<b>Premium Limit:</b> {Config.PREMIUM_USER_LIMIT / (1024**3):.1f}GB\n"
                f"<b>Status:</b> ✅ Online"
            )
            for admin in Config.ADMINS:
                try:
                    await app.send_message(admin, startup_msg)
                except Exception as e:
                    logger.error(f"Failed to send startup message to {admin}: {e}")
    
    except FloodWait as e:
        logger.warning(f"FloodWait: Sleeping for {e.value} seconds...")
        await asyncio.sleep(e.value)
        return await start_bot()
    
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        raise

async def stop_bot():
    """Stop bot gracefully"""
    try:
        # Send shutdown notification to admins
        if Config.ADMINS:
            shutdown_msg = "🤖 <b>Bot Stopped!</b>\n\n<b>Status:</b> ⭕ Offline"
            for admin in Config.ADMINS:
                try:
                    await app.send_message(admin, shutdown_msg)
                except:
                    pass
        
        await app.stop()
        logger.info("✅ Bot stopped successfully!")
    
    except Exception as e:
        logger.error(f"Error stopping bot: {e}")

if __name__ == "__main__":
    # Print startup banner
    print("=" * 60)
    print("🤖 RENAME BOT STARTING...")
    print("=" * 60)
    print(f"📊 Free User Limit: {Config.FREE_USER_LIMIT / (1024**3):.1f}GB")
    print(f"💎 Premium User Limit: {Config.PREMIUM_USER_LIMIT / (1024**3):.1f}GB")
    print(f"⚡ Workers: {Config.WORKERS}")
    print(f"⚡ Sleep Threshold: {Config.SLEEP_THRESHOLD}s")
    print("=" * 60)
    
    # Start Flask server in a separate thread
    print("🌐 Starting health check server...")
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # Run the bot
    try:
        app.run()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Critical error: {e}")
