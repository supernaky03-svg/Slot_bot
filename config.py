import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")
OWNER_ID = int(os.getenv("OWNER_ID", 0))
PORT = int(os.getenv("PORT", 8080))
TZ = "Asia/Yangon"

MAX_BET_LIMIT = 5000000

# Emojis and normalization mapping
ANIMALS = ["🐅", "🐢", "🐔", "🐶", "🐠", "🐍"]
ANIMAL_MAP = {
    "tiger": "🐅", "ကျား": "🐅", "🐅": "🐅",
    "turtle": "🐢", "လိပ်": "🐢", "🐢": "🐢",
    "chicken": "🐔", "ကြက်": "🐔", "🐔": "🐔",
    "dog": "🐶", "ခွေး": "🐶", "🐶": "🐶",
    "fish": "🐠", "ငါး": "🐠", "🐠": "🐠",
    "snake": "🐍", "မြွေ": "🐍", "🐍": "🐍"
}
