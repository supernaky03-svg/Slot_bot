from database.db_manager import db
from game_logic.cache import cache
import logging

async def refund_pending_bets():
    """Refunds all pending memory bets back to DB gracefully on shutdown."""
    async with cache.state_lock:
        if cache.status == "BETTING" and cache.bets:
            logging.info(f"Graceful Shutdown: Refunding {len(cache.bets)} bets.")
            updates = []
            for uid, user_data in cache.users.items():
                updates.append((
                    uid,
                    user_data.balance,
                    user_data.highest_balance,
                    user_data.today_bet_times,
                    user_data.today_betted_amount
                ))
            if updates:
                await db.batch_update_users(updates)
            cache.clear_round_data()

