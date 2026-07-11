import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from database.db_manager import db
from handlers.admin import admin_router
from handlers.member import member_router
from handlers.bets import bet_router
from handlers.callbacks import cb_router
from jobs.scheduler import setup_scheduler
from utils.helpers import dummy_web_server
from game_logic.cache import cache
from game_logic.recovery import refund_pending_bets
from game_logic.engine import start_game_loop

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def on_startup(bot: Bot):
    await db.connect()
    logging.info("Database connected.")
    
    # Load config state
    c = await db.get_config()
    cache.group_id = c["group_id"]
    cache.min_bet = c["min_bet"]
    cache.max_bet = c["max_bet"]
    cache.daily_amount = c["daily_amount"]
    cache.duration = c["duration"]
    cache.is_paused = c["is_paused"]
    cache.is_running = c["is_running"]
    
    setup_scheduler()
    asyncio.create_task(dummy_web_server())
    
    if cache.is_running and cache.group_id:
        logging.info("Resuming active game loop...")
        asyncio.create_task(start_game_loop(bot))

async def on_shutdown(bot: Bot):
    logging.info("Triggering graceful shutdown...")
    await refund_pending_bets()
    await db.close()
    logging.info("Shutdown complete.")

async def main():
    if not BOT_TOKEN:
        logging.error("BOT_TOKEN is missing!")
        sys.exit(1)
        
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    
    dp.include_router(admin_router)
    dp.include_router(member_router)
    dp.include_router(cb_router)
    dp.include_router(bet_router) # Must be last due to generic text handler
    
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped natively.")

