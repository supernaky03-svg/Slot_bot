import asyncpg
import os
from config import DATABASE_URL

class DatabaseManager:
    def __init__(self):
        self.pool = None

    async def connect(self):
        self.pool = await asyncpg.create_pool(DATABASE_URL)
        with open("database/schema.sql", "r") as f:
            await self.pool.execute(f.read())

    async def close(self):
        if self.pool:
            await self.pool.close()

    async def get_config(self):
        async with self.pool.acquire() as conn:
            return await conn.fetchrow("SELECT * FROM group_config WHERE id = 1")

    async def update_config(self, **kwargs):
        set_parts = [f"{k} = ${i+1}" for i, k in enumerate(kwargs.keys())]
        values = list(kwargs.values())
        query = f"UPDATE group_config SET {', '.join(set_parts)} WHERE id = 1"
        async with self.pool.acquire() as conn:
            await conn.execute(query, *values)

    async def get_user(self, user_id: int):
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM users WHERE user_id = $1", user_id)
            if not row:
                await conn.execute("INSERT INTO users (user_id) VALUES ($1) ON CONFLICT DO NOTHING", user_id)
                row = await conn.fetchrow("SELECT * FROM users WHERE user_id = $1", user_id)
            return dict(row)

    async def update_user_balance(self, user_id: int, amount_change: int):
        async with self.pool.acquire() as conn:
            await conn.execute("""
                UPDATE users SET 
                balance = balance + $2,
                highest_balance = GREATEST(highest_balance, balance + $2)
                WHERE user_id = $1
            """, user_id, amount_change)

    async def set_zero_all(self):
        async with self.pool.acquire() as conn:
            await conn.execute("UPDATE users SET balance = 0")

    async def batch_update_users(self, user_data_list):
        # user_data_list format: [(user_id, balance, highest_balance, bet_times, bet_amount), ...]
        async with self.pool.acquire() as conn:
            await conn.executemany("""
                UPDATE users SET 
                    balance = $2, 
                    highest_balance = $3, 
                    today_bet_times = $4, 
                    today_betted_amount = $5
                WHERE user_id = $1
            """, user_data_list)

    async def add_history(self, group_id: int, result: str):
        async with self.pool.acquire() as conn:
            await conn.execute("INSERT INTO round_history (group_id, result) VALUES ($1, $2)", group_id, result)
            # Keep only last 10
            await conn.execute("""
                DELETE FROM round_history WHERE id NOT IN (
                    SELECT id FROM round_history WHERE group_id = $1 ORDER BY id DESC LIMIT 10
                ) AND group_id = $1
            """, group_id)

    async def get_history(self, group_id: int):
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("SELECT result FROM round_history WHERE group_id = $1 ORDER BY id ASC", group_id)
            return [r["result"] for r in rows]

    async def reset_daily_stats(self):
        async with self.pool.acquire() as conn:
            await conn.execute("UPDATE users SET today_bet_times = 0, today_betted_amount = 0")

    async def get_leaderboard(self):
         async with self.pool.acquire() as conn:
             top = await conn.fetch("SELECT user_id, balance FROM users ORDER BY balance DESC LIMIT 10")
             highest = await conn.fetchrow("SELECT user_id, highest_balance FROM users ORDER BY highest_balance DESC LIMIT 1")
             return top, highest

db = DatabaseManager()

