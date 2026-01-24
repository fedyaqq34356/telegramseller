import asyncio
from datetime import datetime
from sqlalchemy import select, and_

from models.subscription import Subscription
from models.user import User
from config.database import get_session


async def start_checker():
    while True:
        try:
            await check_expired_subscriptions()
            await asyncio.sleep(3600)
        except Exception as e:
            print(f"Subscription checker error: {e}")
            await asyncio.sleep(3600)


async def check_expired_subscriptions():
    async with await get_session() as session:
        query = select(Subscription).where(
            and_(
                Subscription.is_active == True,
                Subscription.end_date <= datetime.utcnow()
            )
        )
        result = await session.execute(query)
        expired_subs = result.scalars().all()
        
        for sub in expired_subs:
            sub.is_active = False
            
            query_user = select(User).where(User.user_id == sub.user_id)
            result_user = await session.execute(query_user)
            user = result_user.scalar_one_or_none()
            
            if user:
                try:
                    from main import bot
                    lang = user.language
                    
                    message = """⚠️ Ваша подписка истекла

Тип: {type}
Период: с {start} по {end}

Для продолжения работы приобретите новую подписку.""" if lang == 'ru' else """⚠️ Your subscription has expired

Type: {type}
Period: from {start} to {end}

Purchase a new subscription to continue."""
                    
                    await bot.send_message(
                        user.user_id,
                        message.format(
                            type=sub.subscription_type,
                            start=sub.start_date.strftime('%d.%m.%Y'),
                            end=sub.end_date.strftime('%d.%m.%Y')
                        )
                    )
                except Exception as e:
                    print(f"Error notifying user {sub.user_id}: {e}")
        
        await session.commit()
        
        if expired_subs:
            print(f"Deactivated {len(expired_subs)} expired subscriptions")