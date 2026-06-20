from aiogram import Bot
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.channel import Channel
from config.database import get_session


async def add_channel(
    user_id: int,
    channel_username: str,
    channel_title: str,
    channel_tg_id: int
) -> Channel:
    async with await get_session() as session:
        channel = Channel(
            user_id=user_id,
            channel_username=channel_username,
            channel_title=channel_title,
            channel_tg_id=channel_tg_id
        )
        
        session.add(channel)
        await session.commit()
        await session.refresh(channel)
        
        return channel


async def get_user_channels(user_id: int):
    async with await get_session() as session:
        query = select(Channel).where(Channel.user_id == user_id)
        result = await session.execute(query)
        return result.scalars().all()


    async with await get_session() as session:
        query = select(Channel).where(Channel.channel_id == channel_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()


async def check_bot_permissions(bot: Bot, channel_id: int) -> bool:
    try:
        chat_member = await bot.get_chat_member(channel_id, bot.id)
        
        # Проверяем что бот администратор
        if chat_member.status not in ['administrator', 'creator']:
            return False
        
        # Проверяем необходимые права
        if hasattr(chat_member, 'can_post_messages'):
            return (
                chat_member.can_post_messages and
                chat_member.can_edit_messages and
                chat_member.can_delete_messages
            )
        
        return True
    except Exception:
        return False


async def is_user_subscribed(bot: Bot, channel_id: int, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(channel_id, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception:
        return False


async def remove_user_from_channel(bot: Bot, channel_id: int, user_id: int):
    try:
        await bot.ban_chat_member(channel_id, user_id)
        await bot.unban_chat_member(channel_id, user_id)
        return True
    except Exception:
        return False