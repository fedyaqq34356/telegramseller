import os
from dotenv import load_dotenv

load_dotenv()

# Bot settings
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_IDS = [int(id.strip()) for id in os.getenv('ADMIN_IDS', '').split(',') if id.strip()]

# Database
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite+aiosqlite:///bot.db')

# Crypto Bot
CRYPTO_BOT_TOKEN = os.getenv('CRYPTO_BOT_TOKEN')
CRYPTO_BOT_API_URL = "https://pay.crypt.bot/api"

# Stars
STARS_CHANNEL_LINK = os.getenv('STARS_CHANNEL_LINK', '')

# Other
TIMEZONE = os.getenv('TIMEZONE', 'Europe/Kiev')
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# Limits
FREE_CIRCLES_PER_DAY = 3
FREE_POSTS_PER_DAY = 3
DEMO_DAYS = 1
DEFAULT_REACTION_INTERVAL = 5  # minutes

# Available reactions
AVAILABLE_REACTIONS = ['👍', '❤️', '🔥', '😁', '🎉', '💯', '👏', '😍', '🥰', '😂', '🤩']