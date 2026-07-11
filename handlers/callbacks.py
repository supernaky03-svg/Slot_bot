from aiogram import Router, F
from aiogram.types import CallbackQuery
from game_logic.cache import cache
from database.db_manager import db
import time

cb_router = Router()

@cb_router.callback_query(F.data == "my_info_inline")
async def inline_my_info(callback: CallbackQuery):
    if callback.message.chat.id != cache.group_id: return
    uid = callback.from_user.id
    
    # Cooldown check (5s)
    now = time.time()
    if uid in cache.cooldowns and now - cache.cooldowns[uid] < 5:
        return await callback.answer("Spam မလုပ်ပါနဲ့။", show_alert=True)
    cache.cooldowns[uid] = now
    
    if uid in cache.users:
        bal = cache.users[uid].balance
    else:
        u = await db.get_user(uid)
        bal = u['balance']
        
    await callback.answer(f"💰 သင့်လက်ရှိ Point: {bal}", show_alert=True)

