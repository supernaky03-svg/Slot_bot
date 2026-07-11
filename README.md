# Telegram Slot Game Bot

A high-performance, single-group memory-centric Telegram slot bot.

## Setup
1. Install PostgreSQL and create a database (or use Neon).
2. `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and fill the variables.
4. Run `python main.py`.

## Commands
* Global Admin: `/setGp <group_id>`, `/rmGp`
* Group Admin: `/add`, `/remove`, `/setZero`, `/setmin`, `/setmax`, `/setdaily`, `/startGame`, `/stopGame`, `/paused`, `/resume`
* Members: `/leaderboard`, `/myinfo`, `/daily`
