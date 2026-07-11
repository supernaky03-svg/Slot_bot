from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from database.db_manager import db
from game_logic.cache import cache
from datetime import datetime
import pytz
from config import TZ

member_router = Router()

@member_router.message(Command("leaderboard"))
async def leaderboard(message: Message):
    if message.chat.id != cache.group_id: return
    top, highest = await db.get_leaderboard()
    
    text = "🏆 <b>Leaderboard</b> 🏆\n\n"
    for i, row in enumerate(top, 1):
        text += f"{i}. <code>{row['user_id']}</code> : {row['balance']} pts\n"
        
    if highest:
        text += f"\n🌟 <b>Highest Point Ever:</b>\n<code>{highest['user_id']}</code> : {highest['highest_balance']} pts"
        
    await message.reply(text, parse_mode="HTML")

@member_router.message(Command("myinfo"))
async def my_info(message: Message):
    if message.chat.id != cache.group_id: return
    uid = message.from_user.id
    
    # Check cache first for live balance during betting
    if uid in cache.users:
        u = cache.users[uid]
        bal, high, times = u.balance, u.highest_balance, u.today_bet_times
    else:
        u = await db.get_user(uid)
        bal, high, times = u['balance'], u['highest_balance'], u['today_bet_times']
        
    await message.reply(f"👤 <b>My Info:</b>\n\n"
                        f"💰 Point: {bal}\n"
                        f"📈 Highest: {high}\n"
                        f"🎯 Today Bet Count: {times}", parse_mode="HTML")

@member_router.message(Command("daily"))
async def daily(message: Message):
    if message.chat.id != cache.group_id: return
    uid = message.from_user.id
    u = await db.get_user(uid)
    
    now_date = datetime.now(pytz.timezone(TZ)).date()
    if u['last_daily_claim'] == now_date:
        return await message.reply("❌ ယနေ့အတွက် ယူပြီးပါပြီ။ မနက်ဖြန်မှ ထပ်ယူပါ။")
        
    async with db.pool.acquire() as conn:
        await conn.execute("UPDATE users SET balance = balance + $1, last_daily_claim = $2 WHERE user_id = $3", 
                           cache.daily_amount, now_date, uid)
                           
    await message.reply(f"✅ နေ့စဥ်လက်ဆောင် {cache.daily_amount} Point ရရှိပါသည်။")

