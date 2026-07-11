from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from database.db_manager import db
from config import TZ
import logging

scheduler = AsyncIOScheduler()

async def reset_daily():
    logging.info("Running daily reset for bet times and amounts...")
    await db.reset_daily_stats()
    logging.info("Daily reset complete.")

def setup_scheduler():
    # Make idempotent
    job_id = "daily_reset_job"
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)
        
    scheduler.add_job(
        reset_daily,
        trigger=CronTrigger(hour=0, minute=0, timezone=TZ),
        id=job_id,
        replace_existing=True
    )
    scheduler.start()

