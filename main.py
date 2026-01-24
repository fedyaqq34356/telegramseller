import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from config.settings import BOT_TOKEN
from config.database import create_tables
from handlers import (
    start_handler,
    demo_handler,
    subscription_handler,
    crypto_payment_handler,
    stars_payment_handler,
    channel_handler,
    video_circles_handler,
    post_scheduler_handler,
    settings_handler,
    language_handler
)
from admin import (
    admin_handler,
    broadcast_handler,
    export_handler,
    manual_subscription_handler,
    settings_admin_handler,
    statistics_handler
)
from background_tasks import (
    reaction_worker,
    subscription_checker,
    post_scheduler_worker,
    stats_updater
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()


async def main():
    await create_tables()
    
    dp.include_router(start_handler.router)
    dp.include_router(demo_handler.router)
    dp.include_router(subscription_handler.router)
    dp.include_router(crypto_payment_handler.router)
    dp.include_router(stars_payment_handler.router)
    dp.include_router(channel_handler.router)
    dp.include_router(video_circles_handler.router)
    dp.include_router(post_scheduler_handler.router)
    dp.include_router(settings_handler.router)
    dp.include_router(language_handler.router)
    
    dp.include_router(admin_handler.router)
    dp.include_router(broadcast_handler.router)
    dp.include_router(export_handler.router)
    dp.include_router(manual_subscription_handler.router)
    dp.include_router(settings_admin_handler.router)
    dp.include_router(statistics_handler.router)
    
    asyncio.create_task(reaction_worker.start_worker())
    asyncio.create_task(subscription_checker.start_checker())
    asyncio.create_task(post_scheduler_worker.start_worker())
    asyncio.create_task(stats_updater.start_updater())
    
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())