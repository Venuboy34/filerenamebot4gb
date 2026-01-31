from pyrogram import Client, filters
from pyrogram.types import ForceReply, InlineKeyboardButton, InlineKeyboardMarkup
from database import db
from script import script

@Client.on_message(filters.command("addthumb") & filters.private)
async def add_thumbnail(client, message):
    await message.reply(
        "📸 <b>Send me a photo to set as thumbnail</b>",
        reply_markup=ForceReply(True)
    )

@Client.on_message(filters.photo & filters.private)
async def save_thumbnail(client, message):
    if message.reply_to_message and message.reply_to_message.text:
        if "Send me a photo to set as thumbnail" in message.reply_to_message.text:
            user_id = message.from_user.id
            file_id = message.photo.file_id
            
            await db.set_thumbnail(user_id, file_id)
            await message.reply(script.THUMB_ADDED)
            return

@Client.on_message(filters.command("viewthumb") & filters.private)
async def view_thumbnail(client, message):
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

@Client.on_message(filters.command("deletethumb") & filters.private)
async def delete_thumbnail_cmd(client, message):
    user_id = message.from_user.id
    thumb = await db.get_thumbnail(user_id)
    
    if thumb:
        await db.delete_thumbnail(user_id)
        await message.reply(script.THUMB_DELETED)
    else:
        await message.reply(script.NO_THUMB)
