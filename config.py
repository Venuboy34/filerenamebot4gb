import os

class Config:
    # Bot Configuration
    BOT_TOKEN = "8159032196:AAHcvSp1Y_h5ZXaHSX7-n6H_GoKtFR_VLxk"
    API_ID = 20288994
    API_HASH = "d702614912f1ad370a0d18786002adbf"
    
    # Database
    MONGODB_URL = "mongodb+srv://Zerobothost:zero8907@cluster0.szwdcyb.mongodb.net/?appName=Cluster0"
    
    # Admin
    ADMINS = [8498741978]  # Single admin ID
    # If you need multiple admins, use: ADMINS = [8498741978, admin2_id, admin3_id]
    
    # Force Subscribe
    FORCE_SUB_CHANNELS = [
        "zerodev2",
        "mvxyoffcail"
    ]
    
    # Premium Configuration
    FREE_USER_LIMIT = 2 * 1024 * 1024 * 1024  # 2GB in bytes
    PREMIUM_USER_LIMIT = 4 * 1024 * 1024 * 1024  # 4GB in bytes
    
    # Logs
    PREMIUM_LOGS = -1003712131076
    
    # Images
    FORCE_SUB_IMAGE = "https://i.ibb.co/pr2H8cwT/img-8312532076.jpg"
    WELCOME_IMAGE_API = "https://api.aniwallpaper.workers.dev/random?type=boy"
    
    # Developer
    DEVELOPER = "@Venuboyy"
    OWNER = "@Venuboyy"
    
    # Star Premium Plans (amount in stars: duration)
    STAR_PREMIUM_PLANS = {
        50: "1 month",
        150: "3 months",
        250: "6 months",
        450: "1 year"
    }
    
    # Speed Optimization Settings
    WORKERS = 100
    SLEEP_THRESHOLD = 60
    DOWNLOAD_LOCATION = "/tmp/downloads/"  # Use /tmp for Render
    CHUNK_SIZE = 512 * 1024  # 512KB chunks
    PROGRESS_UPDATE_DELAY = 2  # Update every 2 seconds
    SESSION_NAME = "bot_session"
    WORKDIR = "/tmp"  # Use /tmp for session files on Render
