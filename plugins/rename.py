import os
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
