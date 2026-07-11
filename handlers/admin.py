from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from config import OWNER_ID
from database.db_manager import db
from game_logic.cache import cache
from game_logic.engine import start_game_loop
from utils.helpers import is_admin, get_target_user_id
import asyncio

admin_router = Router()

@admin_router.message(Command("setGp"))
async def set_group(message: Message):
    if message.from_user.id != OWNER_ID: return
    try:
        group_id = int(message.text.split()[1])
        await db.update_config(group_id=group_id)
        cache.group_id = group_id
        await message.reply(f"✅ Group ID {group_id} set successfully.")
    except:
        await message.reply("❌ Invalid format. Use /setGp <group_id>")

@admin_router.message(Command("rmGp"))
async def rm_group(message: Message):
    if message.from_user.id != OWNER_ID: return
    await db.update_config(group_id=None)
    cache.group_id = None
    cache.is_running = False
    await message.reply("✅ Group removed.")

@admin_router.message(Command("add", "remove", "setZero"))
async def manage_points(message: Message, bot: Bot):
    if message.chat.id != cache.group_id: return
    if not await is_admin(bot, message.chat.id, message.from_user.id): return
    
    parts = message.text.split()
    cmd = parts[0].lower()
    
    if cmd == "/setzero":
        if len(parts) != 2: return await message.reply("Format: /setZero target")
        target = parts[1]
    else:
        if len(parts) != 3: return await message.reply("Format: /add amount target")
        try: amount = int(parts[1])
        except: return await message.reply("Invalid amount.")
        target = parts[2]

    if target == "@all":
        if cmd == "/setzero":
            await db.set_zero_all()
        else:
            # Note: @all for add/remove is complex without tracking all DB users.
            # Realistically, you'd execute UPDATE users SET balance = balance +/- amount.
            op = amount if cmd == "/add" else -amount
            async with db.pool.acquire() as conn:
                await conn.execute(f"UPDATE users SET balance = balance + $1, highest_balance = GREATEST(highest_balance, balance + $1)", op)
        await message.reply(f"✅ အားလုံးကို update လုပ်ပြီးပါပြီ။")
        return

    target_id = get_target_user_id(message, target)
    if not target_id: return await message.reply("❌ Target မတွေ့ပါ။")

    if cmd == "/setzero":
        async with db.pool.acquire() as conn:
            await conn.execute("UPDATE users SET balance = 0 WHERE user_id = $1", target_id)
    else:
        op = amount if cmd == "/add" else -amount
        await db.update_user_balance(target_id, op)
        
    await message.reply("✅ လုပ်ဆောင်မှု အောင်မြင်ပါသည်။")

@admin_router.message(Command("setmin", "setmax", "setdaily"))
async def set_limits(message: Message, bot: Bot):
    if message.chat.id != cache.group_id: return
    if not await is_admin(bot, message.chat.id, message.from_user.id): return
    
    parts = message.text.split()
    if len(parts) != 2: return
    try: val = int(parts[1])
    except: return
    
    cmd = parts[0].lower()
    if cmd == "/setmin":
        await db.update_config(min_bet=val)
        cache.min_bet = val
    elif cmd == "/setmax":
        await db.update_config(max_bet=val)
        cache.max_bet = val
    elif cmd == "/setdaily":
        await db.update_config(daily_amount=val)
        cache.daily_amount = val
        
    await message.reply("✅ Setting ပြောင်းလဲခြင်း အောင်မြင်ပါသည်။")

@admin_router.message(Command("startGame"))
async def start_game(message: Message, bot: Bot):
    if message.chat.id != cache.group_id: return
    if not await is_admin(bot, message.chat.id, message.from_user.id): return
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="1 Min", callback_data="dur_60"), InlineKeyboardButton(text="1m 30s", callback_data="dur_90")],
        [InlineKeyboardButton(text="2 Min", callback_data="dur_120"), InlineKeyboardButton(text="3 Min", callback_data="dur_180")]
    ])
    await message.reply("အချိန်ရွေးချယ်ပါ:", reply_markup=kb)

@admin_router.callback_query(F.data.startswith("dur_"))
async def cb_duration(callback: CallbackQuery, bot: Bot):
    if callback.message.chat.id != cache.group_id: return
    if not await is_admin(bot, callback.message.chat.id, callback.from_user.id):
        return await callback.answer("Admin only.", show_alert=True)
        
    dur = int(callback.data.split("_")[1])
    await db.update_config(duration=dur, is_running=True, is_paused=False)
    cache.duration = dur
    cache.is_running = True
    cache.is_paused = False
    
    await callback.message.delete()
    asyncio.create_task(start_game_loop(bot))
    await callback.answer("Game Started!")

@admin_router.message(Command("stopGame", "paused", "resume"))
async def control_game(message: Message, bot: Bot):
    if message.chat.id != cache.group_id: return
    if not await is_admin(bot, message.chat.id, message.from_user.id): return
    
    cmd = message.text.split()[0].lower()
    if cmd == "/stopgame":
        cache.is_running = False
        await db.update_config(is_running=False)
        await message.reply("✅ ဂိမ်းရပ်နားပါပြီ။")
    elif cmd == "/paused":
        cache.is_paused = True
        await db.update_config(is_paused=True)
        await message.reply("✅ ဂိမ်းခေတ္တရပ်ပါပြီ။ (နောက်ပွဲမစတော့ပါ)")
    elif cmd == "/resume":
        cache.is_paused = False
        await db.update_config(is_paused=False)
        await message.reply("✅ ဂိမ်းပြန်လည်စတင်ပါပြီ။")

