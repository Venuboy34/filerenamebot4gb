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
bot = Client(
    "RenameBot",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN
)

# Store file info temporarily
user_files = {}

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

async def get_file_limit(user_id):
    """Get file size limit for user (2GB free, 4GB premium)"""
    user_data = await db.get_user(user_id)
    
    if user_data and user_data.get("expiry_time"):
        expiry = user_data.get("expiry_time")
        if expiry > datetime.datetime.now():
            return Config.PREMIUM_USER_LIMIT  # 4GB for premium
    
    return Config.FREE_USER_LIMIT  # 2GB for free users

@bot.on_message(filters.command("start") & filters.private)
async def start_command(client, message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    
    # Add user to database
    await db.add_user(user_id, user_name)
    
    # Check force sub
    if not await check_force_sub(client, message):
        return
    
    # Get greeting based on time
    greeting = get_greeting()
    
    # Get random welcome image (optimized - no loading animation)
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
    
    # Send welcome message as a reply to the /start command
    await message.reply_photo(
        photo=welcome_image,
        caption=script.START_TXT.format(message.from_user.first_name, greeting),
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@bot.on_message(filters.command("help") & filters.private)
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

@bot.on_message(filters.command("about") & filters.private)
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

@bot.on_message(filters.command("addthumb") & filters.private)
async def add_thumbnail(client, message):
    if not await check_force_sub(client, message):
        return
    
    await message.reply(
        "📸 <b>Send me a photo to set as thumbnail</b>",
        reply_markup=ForceReply(True)
    )

@bot.on_message(filters.photo & filters.private)
async def save_thumbnail(client, message):
    if message.reply_to_message and message.reply_to_message.text:
        if "Send me a photo to set as thumbnail" in message.reply_to_message.text:
            user_id = message.from_user.id
            file_id = message.photo.file_id
            
            await db.set_thumbnail(user_id, file_id)
            await message.reply(script.THUMB_ADDED)
            return

@bot.on_message(filters.command("viewthumb") & filters.private)
async def view_thumbnail(client, message):
    if not await check_force_sub(client, message):
        return
    
    user_id = message.from_user.id
    thumb = await db.get_thumbnail(user_id)
    
    if thumb:
        buttons = [[InlineKeyboardButton("🗑️ Delete Thumbnail", callback_data="delete_thumb")]]
        await message.reply_photo(
            photo=thumb,
            caption="<b>📸 Your Current Thumbnail</b>",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    else:
        await message.reply(script.NO_THUMB)

@bot.on_message(filters.command("deletethumb") & filters.private)
async def delete_thumbnail_cmd(client, message):
    if not await check_force_sub(client, message):
        return
    
    user_id = message.from_user.id
    thumb = await db.get_thumbnail(user_id)
    
    if thumb:
        await db.delete_thumbnail(user_id)
        await message.reply(script.THUMB_DELETED)
    else:
        await message.reply(script.NO_THUMB)

@bot.on_message(filters.document | filters.video | filters.audio)
async def handle_file(client, message):
    if not await check_force_sub(client, message):
        return
    
    user_id = message.from_user.id
    
    # Get file info
    if message.document:
        file = message.document
    elif message.video:
        file = message.video
    elif message.audio:
        file = message.audio
    else:
        return
    
    # Check file size limit
    file_size = file.file_size
    file_limit = await get_file_limit(user_id)
    
    if file_size > file_limit:
        await message.reply(script.FILE_SIZE_ERROR)
        return
    
    # Store file info
    user_files[user_id] = {
        'message': message,
        'file': file,
        'file_size': file_size
    }
    
    # Ask for new filename
    await message.reply(
        f"<b>📝 Current File Name:</b> <code>{file.file_name}</code>\n\n"
        f"<b>📊 File Size:</b> <code>{get_size(file_size)}</code>\n\n"
        f"<b>Send me the new file name (with extension)</b>",
        reply_markup=ForceReply(True)
    )

@bot.on_message(filters.text & filters.private & filters.reply)
async def rename_file(client, message):
    if not await check_force_sub(client, message):
        return
    
    user_id = message.from_user.id
    
    # Check if this is a filename reply
    if user_id not in user_files:
        return
    
    if not message.reply_to_message or not message.reply_to_message.reply_markup:
        return
    
    file_data = user_files[user_id]
    original_message = file_data['message']
    file = file_data['file']
    new_name = message.text
    
    # Get upload mode
    upload_as_doc = await db.get_upload_mode(user_id)
    
    # Get thumbnail
    thumb = await db.get_thumbnail(user_id)
    
    # Start uploading
    status_msg = await message.reply("⏳ <b>Processing your file...</b>")
    
    try:
        # Download file
        await status_msg.edit("📥 <b>Downloading file...</b>")
        file_path = await original_message.download()
        
        # Rename file
        new_path = os.path.join(os.path.dirname(file_path), new_name)
        os.rename(file_path, new_path)
        
        # Upload file
        await status_msg.edit("📤 <b>Uploading renamed file...</b>")
        
        if upload_as_doc:
            await message.reply_document(
                document=new_path,
                thumb=thumb,
                caption=f"<b>✅ File renamed successfully!</b>\n\n<b>New Name:</b> <code>{new_name}</code>",
                progress=progress_callback,
                progress_args=(status_msg,)
            )
        else:
            await message.reply_video(
                video=new_path,
                thumb=thumb,
                caption=f"<b>✅ File renamed successfully!</b>\n\n<b>New Name:</b> <code>{new_name}</code>",
                progress=progress_callback,
                progress_args=(status_msg,)
            )
        
        await status_msg.delete()
        
        # Clean up
        os.remove(new_path)
        del user_files[user_id]
        
    except Exception as e:
        await status_msg.edit(f"❌ <b>Error:</b> {str(e)}")
        if user_id in user_files:
            del user_files[user_id]

async def progress_callback(current, total, status_msg):
    """Progress callback for file upload"""
    try:
        percent = (current / total) * 100
        await status_msg.edit(f"📤 <b>Uploading:</b> {percent:.1f}%")
    except:
        pass

# Callback query handlers
@bot.on_callback_query()
async def callback_handler(client, query):
    data = query.data
    user_id = query.from_user.id
    
    if data == "start":
        greeting = get_greeting()
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
        
        await query.message.edit_media(
            media=InputMediaPhoto(welcome_image),
        )
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
        await query.message.reply(script.THUMB_DELETED)
    
    elif data == "close_data":
        await query.message.delete()
    
    elif data == "check_sub":
        if await check_force_sub(client, query.message):
            await query.message.delete()
            await start_command(client, query.message)

if __name__ == "__main__":
    print("Bot Starting...")
    bot.run()
