import os
import time
import datetime
import asyncio
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
        # Download file with progress (optimized for high speed)
        start_time = time.time()
        
        # Use custom downloader for better speed
        file_path = await fast_download(
            client=client,
            message=original_message,
            status_msg=status_msg,
            start_time=start_time
        )
        
        # Rename file
        new_path = os.path.join(os.path.dirname(file_path), new_name)
        os.rename(file_path, new_path)
        
        # Upload file with progress (optimized for high speed)
        await status_msg.edit("📤 <b>Uploading renamed file...</b>")
        start_time = time.time()
        
        if upload_as_doc:
            await fast_upload_document(
                client=client,
                message=message,
                file_path=new_path,
                thumb=thumb,
                new_name=new_name,
                status_msg=status_msg,
                start_time=start_time
            )
        else:
            await fast_upload_video(
                client=client,
                message=message,
                file_path=new_path,
                thumb=thumb,
                new_name=new_name,
                status_msg=status_msg,
                start_time=start_time
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

async def fast_download(client, message, status_msg, start_time):
    """Optimized download with high-speed settings"""
    
    # Progress tracker
    progress_data = {
        'last_update': 0,
        'start_time': start_time
    }
    
    async def progress_callback(current, total):
        await download_progress(current, total, status_msg, progress_data)
    
    # Download with optimized settings
    file_path = await message.download(
        progress=progress_callback,
        block=True  # Better for large files
    )
    
    return file_path

async def fast_upload_document(client, message, file_path, thumb, new_name, status_msg, start_time):
    """Optimized document upload"""
    
    progress_data = {
        'last_update': 0,
        'start_time': start_time
    }
    
    async def progress_callback(current, total):
        await upload_progress(current, total, status_msg, progress_data)
    
    await message.reply_document(
        document=file_path,
        thumb=thumb,
        caption=f"<b>✅ File renamed successfully!</b>\n\n<b>New Name:</b> <code>{new_name}</code>",
        progress=progress_callback
    )

async def fast_upload_video(client, message, file_path, thumb, new_name, status_msg, start_time):
    """Optimized video upload"""
    
    progress_data = {
        'last_update': 0,
        'start_time': start_time
    }
    
    async def progress_callback(current, total):
        await upload_progress(current, total, status_msg, progress_data)
    
    await message.reply_video(
        video=file_path,
        thumb=thumb,
        caption=f"<b>✅ File renamed successfully!</b>\n\n<b>New Name:</b> <code>{new_name}</code>",
        progress=progress_callback,
        supports_streaming=True
    )

async def download_progress(current, total, status_msg, progress_data):
    """Optimized progress callback for downloads with custom UI"""
    now = time.time()
    
    # Update every 2 seconds to reduce API calls
    if now - progress_data['last_update'] < 2:
        return
    
    progress_data['last_update'] = now
    
    try:
        # Calculate progress
        percentage = (current / total) * 100
        elapsed_time = now - progress_data['start_time']
        speed = current / elapsed_time if elapsed_time > 0 else 0
        
        # Calculate ETA
        if speed > 0:
            eta_seconds = (total - current) / speed
        else:
            eta_seconds = 0
        
        # Format ETA
        eta_min, eta_sec = divmod(int(eta_seconds), 60)
        eta_hr, eta_min = divmod(eta_min, 60)
        
        if eta_hr > 0:
            eta_str = f"{eta_hr} hr, {eta_min} min"
        elif eta_min > 0:
            eta_str = f"{eta_min} min, {eta_sec} sec"
        else:
            eta_str = f"{eta_sec} sec"
        
        # Create progress bar (20 blocks)
        filled_blocks = int(percentage / 5)  # 20 blocks total (100/5)
        progress_bar = "■" * filled_blocks + "□" * (20 - filled_blocks)
        
        # Format message
        progress_text = (
            f"<b>Downloading...</b>\n\n"
            f"<code>{progress_bar}</code>\n\n"
            f"📁 <b>Size :</b> {get_size(current)} | {get_size(total)}\n"
            f"⏳️ <b>Done :</b> {percentage:.2f}%\n"
            f"🚀 <b>Speed :</b> {get_size(speed)}/s\n"
            f"⏰️ <b>ETA :</b> {eta_str}"
        )
        
        await status_msg.edit(progress_text)
        
    except Exception as e:
        pass

async def upload_progress(current, total, status_msg, progress_data):
    """Optimized progress callback for uploads with custom UI"""
    now = time.time()
    
    # Update every 2 seconds to reduce API calls
    if now - progress_data['last_update'] < 2:
        return
    
    progress_data['last_update'] = now
    
    try:
        # Calculate progress
        percentage = (current / total) * 100
        elapsed_time = now - progress_data['start_time']
        speed = current / elapsed_time if elapsed_time > 0 else 0
        
        # Calculate ETA
        if speed > 0:
            eta_seconds = (total - current) / speed
        else:
            eta_seconds = 0
        
        # Format ETA
        eta_min, eta_sec = divmod(int(eta_seconds), 60)
        eta_hr, eta_min = divmod(eta_min, 60)
        
        if eta_hr > 0:
            eta_str = f"{eta_hr} hr, {eta_min} min"
        elif eta_min > 0:
            eta_str = f"{eta_min} min, {eta_sec} sec"
        else:
            eta_str = f"{eta_sec} sec"
        
        # Create progress bar (20 blocks)
        filled_blocks = int(percentage / 5)  # 20 blocks total (100/5)
        progress_bar = "■" * filled_blocks + "□" * (20 - filled_blocks)
        
        # Format message
        progress_text = (
            f"<b>Uploading...</b>\n\n"
            f"<code>{progress_bar}</code>\n\n"
            f"📁 <b>Size :</b> {get_size(current)} | {get_size(total)}\n"
            f"⏳️ <b>Done :</b> {percentage:.2f}%\n"
            f"🚀 <b>Speed :</b> {get_size(speed)}/s\n"
            f"⏰️ <b>ETA :</b> {eta_str}"
        )
        
        await status_msg.edit(progress_text)
        
    except Exception as e:
        pass
