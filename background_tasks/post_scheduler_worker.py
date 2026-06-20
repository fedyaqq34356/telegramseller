import asyncio
import json
from datetime import datetime
from sqlalchemy import select, and_
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from models.settings import PostQueue
from models.channel import Channel
from config.database import get_session


async def start_worker():
    while True:
        try:
            await process_scheduled_posts()
            await asyncio.sleep(60)
        except Exception as e:
            print(f"Post scheduler error: {e}")
            await asyncio.sleep(60)


async def process_scheduled_posts():
    async with await get_session() as session:
        query = select(PostQueue).where(
            and_(
                PostQueue.status == 'pending',
                PostQueue.scheduled_time <= datetime.utcnow()
            )
        )
        result = await session.execute(query)
        posts = result.scalars().all()
        
        for post in posts:
            try:
                query_channel = select(Channel).where(Channel.channel_id == post.channel_id)
                result_channel = await session.execute(query_channel)
                channel = result_channel.scalar_one_or_none()
                
                if not channel:
                    post.status = 'failed'
                    continue
                
                content = json.loads(post.content)
                
                from main import bot
                
                keyboard = None
                if content.get('buttons'):
                    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text=btn['name'], url=btn['url'])]
                        for btn in content['buttons']
                    ])
                
                if post.content_type == 'photo':
                    await bot.send_photo(
                        chat_id=channel.channel_tg_id,
                        photo=content['photo_file_id'],
                        caption=content.get('caption', ''),
                        reply_markup=keyboard
                    )
                elif post.content_type == 'video':
                    await bot.send_video(
                        chat_id=channel.channel_tg_id,
                        video=content['video_file_id'],
                        caption=content.get('caption', ''),
                        reply_markup=keyboard
                    )
                elif post.content_type == 'text':
                    await bot.send_message(
                        chat_id=channel.channel_tg_id,
                        text=content['text'],
                        reply_markup=keyboard
                    )
                
                post.status = 'sent'
                
            except Exception as e:
                print(f"Error sending scheduled post {post.queue_id}: {e}")
                post.status = 'failed'
        
        await session.commit()