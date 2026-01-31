import os

class Config:
    # Bot Configuration
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
    API_ID = int(os.environ.get("API_ID", "12345"))
    API_HASH = os.environ.get("API_HASH", "")
    
    # Database
    MONGODB_URL = os.environ.get("MONGODB_URL", "")
    
    # Admin
    ADMINS = list(set(int(x) for x in os.environ.get("ADMINS", "").split()))
    
    # Force Subscribe
    FORCE_SUB_CHANNELS = [
        "zerodev2",
        "mvxyoffcail"
    ]
    
    # Premium Configuration
    FREE_USER_LIMIT = 2 * 1024 * 1024 * 1024  # 2GB in bytes
    PREMIUM_USER_LIMIT = 4 * 1024 * 1024 * 1024  # 4GB in bytes
    
    # Logs
    PREMIUM_LOGS = int(os.environ.get("PREMIUM_LOGS", "0"))
    
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
