import asyncio
import random
import logging
from aiogram import Bot
from config import ANIMALS
from database.db_manager import db
from game_logic.cache import cache
from game_logic.calculator import calculate_payout
from utils.keyboards import game_reply_kb, result_inline_kb
from utils.helpers import safe_delete_message

async def start_game_loop(bot: Bot):
    while cache.is_running:
        if cache.is_paused:
            await asyncio.sleep(5)
            continue
            
        await start_round(bot)
        
        lock_delay = max(5, cache.duration - 10)
        await asyncio.sleep(lock_delay)
        
        if cache.is_running:
            await lock_round(bot)
            await asyncio.sleep(10)
            
        if cache.is_running:
            await end_round(bot)

async def start_round(bot: Bot):
    async with cache.state_lock:
        cache.status = "BETTING"
        cache.clear_round_data()
    
    msg = await bot.send_message(
        chat_id=cache.group_id,
        text="🎰 ဂိမ်းစတင်ပါပြီ။ လောင်းကြေးထပ်နိုင်ပါပြီ။\n"
             "ပုံစံ - ကျား 100, ကျားကြက် 500",
        reply_markup=game_reply_kb()
    )
    asyncio.create_task(safe_delete_message(msg, delay=cache.duration))

async def lock_round(bot: Bot):
    async with cache.state_lock:
        cache.status = "LOCKED"
        
        if not cache.bets:
            bet_list_str = "လောင်းကြေးမရှိပါ။"
        else:
            lines = [f"{b.user_name}: {''.join(b.animals)} {b.amount}" for b in cache.bets]
            bet_list_str = "\n".join(lines)
            
    msg = await bot.send_message(
        chat_id=cache.group_id,
        text=f"🔒 လောင်းကြေးပိတ်ပါပြီ။\n\n<b>ယခုပွဲလောင်းကြေးများ:</b>\n{bet_list_str}",
        parse_mode="HTML"
    )
    asyncio.create_task(safe_delete_message(msg, delay=15))

async def end_round(bot: Bot):
    results = [random.choice(ANIMALS) for _ in range(3)]
    
    async with cache.state_lock:
        cache.status = "INACTIVE"
        winners = []
        
        # Calculate payouts and apply to memory
        for bet in cache.bets:
            payout = calculate_payout(bet.animals, bet.amount, results)
            if payout > 0:
                user = cache.users[bet.user_id]
                user.balance += payout
                if user.balance > user.highest_balance:
                    user.highest_balance = user.balance
                winners.append((bet, payout))

        # Batch update to DB
        if cache.users:
            updates = []
            for uid, udata in cache.users.items():
                updates.append((uid, udata.balance, udata.highest_balance, udata.today_bet_times, udata.today_betted_amount))
            await db.batch_update_users(updates)
            
    # Save result
    result_str = "".join(results)
    await db.add_history(cache.group_id, result_str)
    hist = await db.get_history(cache.group_id)
    hist_str = " | ".join(hist[-10:])
    
    # Format winner announcement
    win_str = "\n".join([f"🎉 {b.user_name}: {''.join(b.animals)} (+{p})" for b, p in winners])
    if not win_str: win_str = "အနိုင်ရသူမရှိပါ။"

    text = f"🎲 <b>ရလဒ်:</b> {result_str}\n\n" \
           f"<b>အနိုင်ရသူများ:</b>\n{win_str}\n\n" \
           f"〰️〰️〰️〰️〰️〰️〰️\n" \
           f"<b>ယခင်ရလဒ်များ:</b>\n{hist_str}"
           
    await bot.send_message(
        chat_id=cache.group_id,
        text=text,
        parse_mode="HTML",
        reply_markup=result_inline_kb()
    )

