import time
import datetime
import asyncio
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, PeerIdInvalid

class temp:
    B_USERS_CANCEL = False
    B_GROUPS_CANCEL = False
    B_LINK = ""

async def get_seconds(time_str):
    """Convert time string to seconds"""
    try:
        parts = time_str.split()
        if len(parts) != 2:
            return 0
        
        value = int(parts[0])
        unit = parts[1].lower()
        
        if unit in ['minute', 'minutes', 'min', 'mins']:
            return value * 60
        elif unit in ['hour', 'hours', 'hr', 'hrs']:
            return value * 3600
        elif unit in ['day', 'days']:
            return value * 86400
        elif unit in ['week', 'weeks']:
            return value * 604800
        elif unit in ['month', 'months']:
            return value * 2592000  # 30 days
        elif unit in ['year', 'years']:
            return value * 31536000  # 365 days
        else:
            return 0
    except:
        return 0

def get_readable_time(seconds):
    """Convert seconds to readable time format"""
    periods = [
        ('year', 60*60*24*365),
        ('month', 60*60*24*30),
        ('day', 60*60*24),
        ('hour', 60*60),
        ('minute', 60),
        ('second', 1)
    ]
    
    strings = []
    for period_name, period_seconds in periods:
        if seconds >= period_seconds:
            period_value, seconds = divmod(seconds, period_seconds)
            if period_value > 0:
                strings.append(f"{int(period_value)} {period_name}{'s' if period_value > 1 else ''}")
    
    return ', '.join(strings[:2]) if strings else '0 seconds'

def get_size(size):
    """Get size in readable format"""
    units = ["Bytes", "KB", "MB", "GB", "TB"]
    size = float(size)
    i = 0
    while size >= 1024.0 and i < len(units)-1:
        i += 1
        size /= 1024.0
    return f"{size:.2f} {units[i]}"

async def users_broadcast(user_id, message, pin):
    """Broadcast message to user"""
    try:
        if pin:
            await message.copy(chat_id=user_id)
            return True, "Success"
        else:
            await message.copy(chat_id=user_id)
            return True, "Success"
    except FloodWait as e:
        await asyncio.sleep(e.x)
        return await users_broadcast(user_id, message, pin)
    except UserIsBlocked:
        return False, "Blocked"
    except InputUserDeactivated:
        return False, "Deleted"
    except PeerIdInvalid:
        return False, "Error"
    except Exception as e:
        return False, "Error"

async def groups_broadcast(chat_id, message, pin):
    """Broadcast message to group"""
    try:
        await message.copy(chat_id=chat_id)
        if pin:
            try:
                await message.pin(chat_id=chat_id, disable_notification=True)
            except:
                pass
        return "Success"
    except FloodWait as e:
        await asyncio.sleep(e.x)
        return await groups_broadcast(chat_id, message, pin)
    except Exception as e:
        return "Error"

async def clear_junk(user_id, message):
    """Check if user is active"""
    try:
        await message.copy(chat_id=user_id)
        return True, "Active"
    except UserIsBlocked:
        return False, "Blocked"
    except InputUserDeactivated:
        return False, "Deleted"
    except Exception as e:
        return False, "Error"

async def junk_group(chat_id, message):
    """Check if group is active"""
    try:
        await message.copy(chat_id=chat_id)
        return True, "active", ""
    except Exception as e:
        return False, "deleted", str(e)
