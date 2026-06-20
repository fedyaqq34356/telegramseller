from datetime import datetime, date
from models.settings import CirclesUsage, PostingUsage
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from config.database import get_session


async def check_daily_limit(user_id: int, feature: str, limit: int) -> bool:
    async with await get_session() as session:
        today = date.today()
        
        if feature == 'circles':
            query = select(func.sum(CirclesUsage.count)).where(
                CirclesUsage.user_id == user_id,
                func.date(CirclesUsage.date) == today
            )
        elif feature == 'posting':
            query = select(func.sum(PostingUsage.count)).where(
                PostingUsage.user_id == user_id,
                func.date(PostingUsage.date) == today
            )
        else:
            return False
        
        result = await session.execute(query)
        count = result.scalar() or 0
        
        return count < limit


async def increment_usage(user_id: int, feature: str):
    async with await get_session() as session:
        if feature == 'circles':
            usage = CirclesUsage(user_id=user_id, count=1)
        elif feature == 'posting':
            usage = PostingUsage(user_id=user_id, count=1)
        else:
            return
        
        session.add(usage)
        await session.commit()


def format_datetime(dt: datetime) -> str:
    return dt.strftime('%d.%m.%Y %H:%M')


async def get_admin_setting(key: str, default: str = '') -> str:
    from models.settings import AdminSettings
    
    async with await get_session() as session:
        query = select(AdminSettings).where(AdminSettings.setting_key == key)
        result = await session.execute(query)
        setting = result.scalar_one_or_none()
        
        if setting:
            return setting.setting_value
        return default


async def set_admin_setting(key: str, value: str):
    from models.settings import AdminSettings
    
    async with await get_session() as session:
        query = select(AdminSettings).where(AdminSettings.setting_key == key)
        result = await session.execute(query)
        setting = result.scalar_one_or_none()
        
        if setting:
            setting.setting_value = value
            setting.last_updated = datetime.utcnow()
        else:
            setting = AdminSettings(
                setting_key=key,
                setting_value=value
            )
            session.add(setting)
        
        await session.commit()