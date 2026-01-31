import os
import time
import datetime
from pyrogram import Client, filters
from pyrogram.types import ForceReply
from config import Config
from database import db
from script import script
from utils import get_size

# Store file info temporarily
user_files = {}

async def get_file_limit(user_id):
    """Get file size limit for user (2GB free, 4GB premium)"""
    user_data = await db.get_user(user_id)
    
    if user_data and user_data.get("expiry_time"):
        expiry = user_data.get("expiry_time")
        if expiry > datetime.datetime.now():
            return Config.PREMIUM_USER_LIMIT  # 4GB for premium
    
    return Config.FREE_USER_LIMIT  # 2GB for free users

@Client.on_message((filters.document | filters.video | filters.audio) & filters.private)
async def handle_file(client, message):
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

@Client.on_message(filters.text & filters.private & filters.reply)
async def rename_file(client, message):
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
    
    # Start processing
    status_msg = await message.reply("⏳ <b>Processing your file...</b>")
    
    try:
        # Download file with progress
        start_time = time.time()
        file_path = await original_message.download(
            progress=download_progress,
            progress_args=(status_msg, start_time)
        )
        
        # Rename file
        new_path = os.path.join(os.path.dirname(file_path), new_name)
        os.rename(file_path, new_path)
        
        # Upload file with progress
        await status_msg.edit("📤 <b>Uploading renamed file...</b>")
        start_time = time.time()
        
        if upload_as_doc:
            await message.reply_document(
                document=new_path,
                thumb=thumb,
                caption=f"<b>✅ File renamed successfully!</b>\n\n<b>New Name:</b> <code>{new_name}</code>",
                progress=upload_progress,
                progress_args=(status_msg, start_time)
            )
        else:
            await message.reply_video(
                video=new_path,
                thumb=thumb,
                caption=f"<b>✅ File renamed successfully!</b>\n\n<b>New Name:</b> <code>{new_name}</code>",
                progress=upload_progress,
                progress_args=(status_msg, start_time)
            )
        
        await status_msg.delete()
        
        # Clean up
        try:
            os.remove(new_path)
        except:
            pass
        del user_files[user_id]
        
    except Exception as e:
        await status_msg.edit(f"❌ <b>Error:</b> {str(e)}")
        if user_id in user_files:
            del user_files[user_id]

async def download_progress(current, total, status_msg, start_time):
    """Progress callback for file download with speed and ETA"""
    now = time.time()
    diff = now - start_time
    
    if diff < 1:
        return
    
    try:
        percentage = current * 100 / total
        speed = current / diff
        elapsed_time = round(diff)
        
        if current == total:
            return
        
        eta = round((total - current) / speed)
        
        # Format time
        def time_formatter(seconds):
            minutes, seconds = divmod(seconds, 60)
            hours, minutes = divmod(minutes, 60)
            days, hours = divmod(hours, 24)
            
            tmp = ""
            if days:
                tmp += f"{days}d "
            if hours:
                tmp += f"{hours}h "
            if minutes:
                tmp += f"{minutes}m "
            if seconds:
                tmp += f"{seconds}s"
            return tmp.strip()
        
        progress_str = "".join(["█" if i <= percentage / 10 else "░" for i in range(10)])
        
        tmp = (
            f"📥 <b>Downloading...</b>\n\n"
            f"<code>{progress_str}</code> {percentage:.1f}%\n\n"
            f"<b>Total Size:</b> {get_size(total)}\n"
            f"<b>Downloaded:</b> {get_size(current)}\n"
            f"<b>Speed:</b> {get_size(speed)}/s\n"
            f"<b>ETA:</b> {time_formatter(eta)}\n"
            f"<b>Elapsed:</b> {time_formatter(elapsed_time)}"
        )
        
        await status_msg.edit(tmp)
    except Exception as e:
        pass

async def upload_progress(current, total, status_msg, start_time):
    """Progress callback for file upload with speed and ETA"""
    now = time.time()
    diff = now - start_time
    
    if diff < 1:
        return
    
    try:
        percentage = current * 100 / total
        speed = current / diff
        elapsed_time = round(diff)
        
        if current == total:
            return
        
        eta = round((total - current) / speed)
        
        # Format time
        def time_formatter(seconds):
            minutes, seconds = divmod(seconds, 60)
            hours, minutes = divmod(minutes, 60)
            days, hours = divmod(hours, 24)
            
            tmp = ""
            if days:
                tmp += f"{days}d "
            if hours:
                tmp += f"{hours}h "
            if minutes:
                tmp += f"{minutes}m "
            if seconds:
                tmp += f"{seconds}s"
            return tmp.strip()
        
        progress_str = "".join(["█" if i <= percentage / 10 else "░" for i in range(10)])
        
        tmp = (
            f"📤 <b>Uploading...</b>\n\n"
            f"<code>{progress_str}</code> {percentage:.1f}%\n\n"
            f"<b>Total Size:</b> {get_size(total)}\n"
            f"<b>Uploaded:</b> {get_size(current)}\n"
            f"<b>Speed:</b> {get_size(speed)}/s\n"
            f"<b>ETA:</b> {time_formatter(eta)}\n"
            f"<b>Elapsed:</b> {time_formatter(elapsed_time)}"
        )
        
        await status_msg.edit(tmp)
    except Exception as e:
        pass
