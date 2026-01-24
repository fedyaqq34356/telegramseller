import json
from datetime import datetime
from sqlalchemy import select

from models.settings import PostQueue
from config.database import get_session


async def schedule_post(
    user_id: int,
    channel_id: int,
    content_type: str,
    content: dict,
    scheduled_time: datetime
):
    async with await get_session() as session:
        post = PostQueue(
            user_id=user_id,
            channel_id=channel_id,
            content_type=content_type,
            content=json.dumps(content, ensure_ascii=False),
            scheduled_time=scheduled_time,
            status='pending'
        )
        
        session.add(post)
        await session.commit()
        await session.refresh(post)
        
        return post


async def get_pending_posts(user_id: int):
    async with await get_session() as session:
        query = select(PostQueue).where(
            PostQueue.user_id == user_id,
            PostQueue.status == 'pending'
        ).order_by(PostQueue.scheduled_time)
        
        result = await session.execute(query)
        return result.scalars().all()


async def cancel_scheduled_post(queue_id: int):
    async with await get_session() as session:
        query = select(PostQueue).where(PostQueue.queue_id == queue_id)
        result = await session.execute(query)
        post = result.scalar_one_or_none()
        
        if post:
            post.status = 'cancelled'
            await session.commit()
            return True
        
        return False