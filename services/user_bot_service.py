from aiogram import Bot
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.channel import UserBot
from config.database import get_session


async def validate_bot_token(token: str) -> dict:
    try:
        bot = Bot(token=token)
        bot_info = await bot.get_me()
        await bot.session.close()
        
        return {
            'valid': True,
            'username': bot_info.username,
            'id': bot_info.id
        }
    except Exception:
        return {'valid': False}


async def save_user_bot(user_id: int, bot_token: str, bot_username: str) -> UserBot:
    async with await get_session() as session:
        user_bot = UserBot(
            user_id=user_id,
            bot_token=bot_token,
            bot_username=bot_username,
            is_active=True
        )
        
        session.add(user_bot)
        await session.commit()
        await session.refresh(user_bot)
        
        return user_bot


async def get_user_bot(user_id: int):
    async with await get_session() as session:
        query = select(UserBot).where(
            UserBot.user_id == user_id,
            UserBot.is_active == True
        )
        result = await session.execute(query)
        return result.scalar_one_or_none()