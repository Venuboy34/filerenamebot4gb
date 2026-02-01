import asyncio
import datetime
import pytz
import requests
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ForceReply, InputMediaPhoto, CallbackQuery
from config import Config
from database import db
from script import script

def get_greeting():
    """Get time-based greeting with emoji - Works for both India (IST) and Sri Lanka (SLST)"""
    # Both India (IST) and Sri Lanka (SLST) are UTC+5:30, so using Asia/Kolkata works for both
    # You can also use 'Asia/Colombo' for Sri Lanka - both are the same timezone
    timezone = pytz.timezone('Asia/Kolkata')  # Same as Asia/Colombo (UTC+5:30)
    current_hour = datetime.datetime.now(timezone).hour
    
    if 5 <= current_hour < 12:
        return "Good Morning 🌞"
    elif 12 <= current_hour < 19:
        return "Good Afternoon ☀️"
    else:
        return "Good Night 🌚"

def get_random_image():
    """Get random welcome image with fallback"""
    try:
        # Try to get image from your API with timeout
        response = requests.get(Config.WELCOME_IMAGE_API, timeout=3, allow_redirects=True)
        if response.status_code == 200:
            return response.url
    except:
        pass
    
    # Fallback to alternative random image APIs
    fallback_urls = [
        "https://api.aniwallpaper.workers.dev/random?type=boy",
        "https://picsum.photos/800/600",
        "https://source.unsplash.com/random/800x600"
    ]
    
    for url in fallback_urls:
        try:
            response = requests.head(url, timeout=2)
            if response.status_code == 200:
                return url
        except:
            continue
    
    # Ultimate fallback - a static image
    return "https://picsum.photos/800/600"

async def check_force_sub(client, message):
    """Check if user has joined force sub channels"""
    user_id = message.from_user.id
    
    for channel in Config.FORCE_SUB_CHANNELS:
        try:
            member = await client.get_chat_member(f"@{channel}", user_id)
            if member.status in ["kicked", "left"]:
                buttons = []
                for ch in Config.FORCE_SUB_CHANNELS:
                    buttons.append([InlineKeyboardButton(f"Join @{ch}", url=f"https://t.me/{ch}")])
                buttons.append([InlineKeyboardButton("🔄 Try Again", callback_data="check_sub")])
                
                await message.reply_photo(
                    photo=Config.FORCE_SUB_IMAGE,
                    caption=script.FORCE_SUB_TEXT,
                    reply_markup=InlineKeyboardMarkup(buttons)
                )
                return False
        except Exception as e:
            print(f"Force sub check error: {e}")
            continue
    
    return True

@Client.on_message(filters.command("start") & filters.private)
async def start_command(client, message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    
    # Add user to database
    await db.add_user(user_id, user_name)
    
    # Check force sub
    if not await check_force_sub(client, message):
        return
    
    # Show loading animation
    loading_msg = await message.reply("⚡")
    await asyncio.sleep(2)
    await loading_msg.delete()
    
    # Get greeting based on time (NEW FEATURE)
    greeting = get_greeting()
    
    # Get random welcome image (NEW FEATURE - optimized with fallbacks)
    welcome_image = get_random_image()
    
    # Create buttons
    buttons = [
        [
            InlineKeyboardButton("📚 Help", callback_data="help"),
            InlineKeyboardButton("ℹ️ About", callback_data="about")
        ],
        [
            InlineKeyboardButton("💎 Premium", callback_data="premium_info"),
            InlineKeyboardButton("⚙️ Settings", callback_data="settings")
        ],
        [
            InlineKeyboardButton("👨‍💻 Developer", url=f"https://t.me/{Config.DEVELOPER.replace('@', '')}")
        ]
    ]
    
    # Send welcome message (UPDATED - using greeting instead of "👋")
    await message.reply_photo(
        photo=welcome_image,
        caption=script.START_TXT.format(message.from_user.first_name, greeting),
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@Client.on_message(filters.command("help") & filters.private)
async def help_command(client, message):
    if not await check_force_sub(client, message):
        return
    
    buttons = [
        [InlineKeyboardButton("🏠 Home", callback_data="start")],
        [InlineKeyboardButton("🚫 Close", callback_data="close_data")]
    ]
    
    await message.reply(
        script.HELP_TXT,
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@Client.on_message(filters.command("about") & filters.private)
async def about_command(client, message):
    if not await check_force_sub(client, message):
        return
    
    me = await client.get_me()
    buttons = [
        [InlineKeyboardButton("🏠 Home", callback_data="start")],
        [InlineKeyboardButton("🚫 Close", callback_data="close_data")]
    ]
    
    await message.reply(
        script.ABOUT_TXT.format(me.username, me.first_name),
        reply_markup=InlineKeyboardMarkup(buttons),
        disable_web_page_preview=True
    )

@Client.on_callback_query()
async def callback_handler(client, query: CallbackQuery):
    data = query.data
    user_id = query.from_user.id
    
    if data == "start":
        # Get greeting based on time (NEW FEATURE)
        greeting = get_greeting()
        
        # Get random welcome image (NEW FEATURE - optimized with fallbacks)
        welcome_image = get_random_image()
        
        buttons = [
            [
                InlineKeyboardButton("📚 Help", callback_data="help"),
                InlineKeyboardButton("ℹ️ About", callback_data="about")
            ],
            [
                InlineKeyboardButton("💎 Premium", callback_data="premium_info"),
                InlineKeyboardButton("⚙️ Settings", callback_data="settings")
            ],
            [
                InlineKeyboardButton("👨‍💻 Developer", url=f"https://t.me/{Config.DEVELOPER.replace('@', '')}")
            ]
        ]
        
        try:
            await query.message.edit_media(
                media=InputMediaPhoto(welcome_image, caption=script.START_TXT.format(query.from_user.first_name, greeting)),
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        except:
            await query.message.edit_caption(
                caption=script.START_TXT.format(query.from_user.first_name, greeting),
                reply_markup=InlineKeyboardMarkup(buttons)
            )
    
    elif data == "help":
        buttons = [
            [InlineKeyboardButton("🏠 Home", callback_data="start")],
            [InlineKeyboardButton("🚫 Close", callback_data="close_data")]
        ]
        await query.message.edit_caption(
            caption=script.HELP_TXT,
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    
    elif data == "about":
        me = await client.get_me()
        buttons = [
            [InlineKeyboardButton("🏠 Home", callback_data="start")],
            [InlineKeyboardButton("🚫 Close", callback_data="close_data")]
        ]
        await query.message.edit_caption(
            caption=script.ABOUT_TXT.format(me.username, me.first_name),
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    
    elif data == "premium_info" or data == "buy_info":
        buttons = [
            [InlineKeyboardButton("1 Month - 50⭐", callback_data="buy_50")],
            [InlineKeyboardButton("3 Months - 150⭐", callback_data="buy_150")],
            [InlineKeyboardButton("6 Months - 250⭐", callback_data="buy_250")],
            [InlineKeyboardButton("1 Year - 450⭐", callback_data="buy_450")],
            [InlineKeyboardButton("🏠 Home", callback_data="start")]
        ]
        await query.message.edit_caption(
            caption=script.PREMIUM_TXT,
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    
    elif data == "settings":
        upload_mode = await db.get_upload_mode(user_id)
        mode_text = "📄 Document" if upload_mode else "🎥 Video"
        
        buttons = [
            [InlineKeyboardButton(
                f"Upload as: {mode_text}",
                callback_data="toggle_upload_mode"
            )],
            [InlineKeyboardButton("🏠 Home", callback_data="start")]
        ]
        await query.message.edit_caption(
            caption="<b>⚙️ Settings</b>\n\nChoose your upload preference:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    
    elif data == "toggle_upload_mode":
        current_mode = await db.get_upload_mode(user_id)
        new_mode = not current_mode
        await db.set_upload_mode(user_id, new_mode)
        
        mode_text = "📄 Document" if new_mode else "🎥 Video"
        buttons = [
            [InlineKeyboardButton(
                f"Upload as: {mode_text}",
                callback_data="toggle_upload_mode"
            )],
            [InlineKeyboardButton("🏠 Home", callback_data="start")]
        ]
        await query.message.edit_caption(
            caption="<b>⚙️ Settings</b>\n\nChoose your upload preference:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        await query.answer(f"✅ Upload mode changed to {mode_text}", show_alert=True)
    
    elif data == "delete_thumb":
        await db.delete_thumbnail(user_id)
        await query.message.delete()
        await client.send_message(user_id, script.THUMB_DELETED)
    
    elif data == "close_data":
        await query.message.delete()
    
    elif data == "check_sub":
        if await check_force_sub(client, query.message):
            await query.message.delete()
            await start_command(client, query.message)
