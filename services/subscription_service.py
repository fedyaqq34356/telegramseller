from datetime import datetime, timedelta
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from models.subscription import Subscription
from config.database import get_session


async def check_user_subscription(user_id: int, subscription_type: str = None) -> bool:
    async with await get_session() as session:
        query = select(Subscription).where(
            and_(
                Subscription.user_id == user_id,
                Subscription.is_active == True,
                Subscription.end_date > datetime.utcnow()
            )
        )
        
        if subscription_type:
            query = query.where(Subscription.subscription_type == subscription_type)
        
        result = await session.execute(query)
        subscription = result.scalar_one_or_none()
        
        return subscription is not None


async def get_active_subscription(user_id: int, subscription_type: str = None):
    async with await get_session() as session:
        query = select(Subscription).where(
            and_(
                Subscription.user_id == user_id,
                Subscription.is_active == True,
                Subscription.end_date > datetime.utcnow()
            )
        )
        
        if subscription_type:
            query = query.where(Subscription.subscription_type == subscription_type)
        
        result = await session.execute(query)
        return result.scalar_one_or_none()


async def create_subscription(
    user_id: int,
    subscription_type: str,
    period_months: int,
    tariff: str = None
) -> Subscription:
    async with await get_session() as session:
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=period_months * 30)
        
        subscription = Subscription(
            user_id=user_id,
            subscription_type=subscription_type,
            tariff=tariff,
            start_date=start_date,
            end_date=end_date,
            is_active=True
        )
        
        session.add(subscription)
        await session.commit()
        await session.refresh(subscription)
        
        return subscription


async def get_user_subscriptions(user_id: int):
    async with await get_session() as session:
        query = select(Subscription).where(
            and_(
                Subscription.user_id == user_id,
                Subscription.is_active == True,
                Subscription.end_date > datetime.utcnow()
            )
        )
        
        result = await session.execute(query)
        return result.scalars().all()


async def deactivate_subscription(subscription_id: int):
    async with await get_session() as session:
        query = select(Subscription).where(Subscription.subscription_id == subscription_id)
        result = await session.execute(query)
        subscription = result.scalar_one_or_none()
        
        if subscription:
            subscription.is_active = False
            await session.commit()