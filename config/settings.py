import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_IDS = [int(id.strip()) for id in os.getenv('ADMIN_IDS', '').split(',') if id.strip()]

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite+aiosqlite:///bot.db')

CRYPTO_BOT_TOKEN = os.getenv('CRYPTO_BOT_TOKEN')
CRYPTO_BOT_API_URL = "https://pay.crypt.bot/api"

STARS_CHANNEL_LINK = os.getenv('STARS_CHANNEL_LINK', '')

TELETHON_API_ID = int(os.getenv('TELETHON_API_ID', '0'))
TELETHON_API_HASH = os.getenv('TELETHON_API_HASH', '')

TIMEZONE = os.getenv('TIMEZONE', 'Europe/Kiev')
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

FREE_CIRCLES_PER_DAY = 3
FREE_POSTS_PER_DAY = 3
DEMO_DAYS = 1
DEFAULT_REACTION_INTERVAL = 5

AVAILABLE_REACTIONS = ['👍', '❤️', '🔥', '😁', '🎉', '💯', '👏', '😍', '🥰', '😂', '🤩']