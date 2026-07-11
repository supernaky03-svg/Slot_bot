from aiogram import Router, F
from aiogram.types import Message
from game_logic.cache import cache, Bet, UserCacheData
from game_logic.parser import parse_bet_string
from database.db_manager import db
from utils.helpers import safe_delete_message
import asyncio

bet_router = Router()
bet_router.edited_message.handlers.clear() # Ignore edits completely

@bet_router.message(F.text & ~F.text.startswith("/"))
async def handle_text(message: Message):
    if message.chat.id != cache.group_id: return
    
    uid = message.from_user.id
    name = message.from_user.full_name
    text = message.text.strip()
    
    cache.username_to_id[message.from_user.username or ""] = uid
    cache.username_to_id[name] = uid
    
    # Handle ReplyKeyboard clicks
    if text == "My Info":
        # Reply handled inside member.py /myinfo or we can duplicate logic. Better to route or handle locally:
        u = cache.users.get(uid)
        if not u: 
            du = await db.get_user(uid)
            bal, high = du['balance'], du['highest_balance']
        else:
            bal, high = u.balance, u.highest_balance
        msg = await message.reply(f"💰 Point: {bal} | 📈 Highest: {high}")
        asyncio.create_task(safe_delete_message(msg, 10))
        asyncio.create_task(safe_delete_message(message, 1))
        return
        
    if text == "My Bets":
        u = cache.users.get(uid)
        if not u: 
            du = await db.get_user(uid)
            count, amt = du['today_bet_times'], du['today_betted_amount']
        else:
            count, amt = u.today_bet_times, u.today_betted_amount
        msg = await message.reply(f"🎯 Today Count: {count} | 💸 Total Amt: {amt}")
        asyncio.create_task(safe_delete_message(msg, 10))
        asyncio.create_task(safe_delete_message(message, 1))
        return
        
    if text == "လောင်းခြင်းပယ်ဖျက်":
        asyncio.create_task(safe_delete_message(message, 1))
        async with cache.state_lock:
            if cache.status != "BETTING":
                msg = await message.reply("❌ လောင်းကြေးပယ်ဖျက်၍ မရတော့ပါ။")
                asyncio.create_task(safe_delete_message(msg, 5))
                return
            
            refund = sum(b.amount for b in cache.bets if b.user_id == uid)
            if refund > 0:
                cache.bets = [b for b in cache.bets if b.user_id != uid]
                cache.users[uid].balance += refund
                cache.users[uid].today_bet_times -= 1
                cache.users[uid].today_betted_amount -= refund
                msg = await message.reply("✅ လောင်းကြေးများ ပယ်ဖျက်ပြီးပါပြီ။")
            else:
                msg = await message.reply("❌ ပယ်ဖျက်ရန် လောင်းကြေးမရှိပါ။")
            asyncio.create_task(safe_delete_message(msg, 5))
        return

    # Normal Betting Flow
    if cache.status == "INACTIVE":
        return # Ignore regular chat when game off

    if cache.status == "LOCKED":
        asyncio.create_task(safe_delete_message(message, 1))
        return

    # We are in BETTING state
    animals, amount = parse_bet_string(text)
    if not animals:
        asyncio.create_task(safe_delete_message(message, 1))
        return # Not a valid bet, auto-delete silently

    # Format is valid, try placing bet
    async with cache.state_lock:
        # Load user to memory if not there
        if uid not in cache.users:
            u = await db.get_user(uid)
            cache.users[uid] = UserCacheData(
                balance=u['balance'],
                highest_balance=u['highest_balance'],
                today_bet_times=u['today_bet_times'],
                today_betted_amount=u['today_betted_amount'],
                user_name=name
            )
            
        user = cache.users[uid]
        
        if amount < cache.min_bet or amount > cache.max_bet:
            msg = await message.reply(f"❌ လောင်းကြေး {cache.min_bet} မှ {cache.max_bet} အတွင်းသာရမည်။")
            asyncio.create_task(safe_delete_message(msg, 5))
            return
            
        if user.balance < amount:
            msg = await message.reply("❌ Point မလုံလောက်ပါ။")
            asyncio.create_task(safe_delete_message(msg, 5))
            return
            
        # Deduct and register bet
        user.balance -= amount
        user.today_bet_times += 1
        user.today_betted_amount += amount
        cache.bets.append(Bet(uid, name, animals, amount))
        
    msg = await message.reply(f"✅ {''.join(animals)} {amount} လောင်းခြင်း အောင်မြင်ပါသည်။")
    asyncio.create_task(safe_delete_message(msg, 10))

