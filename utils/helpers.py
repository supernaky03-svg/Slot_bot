import asyncio
import time
import logging
from aiogram import Bot
from aiogram.types import Message
from aiogram.exceptions import TelegramRetryAfter, TelegramBadRequest
from game_logic.cache import cache
from aiohttp import web
import os

async def safe_delete_message(message: Message, delay: int = 0):
    if delay > 0:
        await asyncio.sleep(delay)
    try:
        await message.delete()
    except TelegramRetryAfter as e:
        await asyncio.sleep(e.retry_after)
        await safe_delete_message(message, 0)
    except TelegramBadRequest:
        pass # Message already deleted or not found
    except Exception as e:
        logging.error(f"Error deleting msg: {e}")

async def is_admin(bot: Bot, chat_id: int, user_id: int) -> bool:
    from config import OWNER_ID
    if user_id == OWNER_ID: return True
    
    now = time.time()
    # Cache admins for 30 mins (1800s) to avoid FloodWait
    if "admin_fetch_time" not in cache.__dict__ or now - cache.__dict__.get("admin_fetch_time", 0) > 1800:
        try:
            admins = await bot.get_chat_administrators(chat_id)
            cache.admin_cache = {a.user.id: now for a in admins}
            cache.__dict__["admin_fetch_time"] = now
        except Exception:
            return False
            
    return user_id in cache.admin_cache

def get_target_user_id(message: Message, target: str):
    if message.entities:
        for ent in message.entities:
            if ent.type == "text_mention" and ent.user:
                return ent.user.id
                
    if target.startswith("@"):
        un = target[1:]
        return cache.username_to_id.get(un)
        
    try:
        return int(target)
    except:
        return cache.username_to_id.get(target)

async def dummy_web_server():
    from config import PORT
    app = web.Application()
    app.router.add_get('/', lambda r: web.Response(text="Bot is running!"))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    logging.info(f"Dummy web server started on port {PORT}")

