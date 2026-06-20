import asyncio
import random
from datetime import datetime
from sqlalchemy import select, and_
from telethon import TelegramClient, events
from telethon.tl.functions.messages import SendReactionRequest
from telethon.tl.types import ReactionEmoji

from models.channel import UserBot, ReactionsSettings, Channel
from models.subscription import Subscription
from config.database import get_session
from config.settings import AVAILABLE_REACTIONS

active_clients = {}


async def start_worker():
    while True:
        try:
            await check_and_start_bots()
            await asyncio.sleep(60)
        except Exception as e:
            print(f"Reaction worker error: {e}")
            await asyncio.sleep(60)


async def check_and_start_bots():
    async with await get_session() as session:
        query = select(UserBot).where(UserBot.is_active == True)
        result = await session.execute(query)
        user_bots = result.scalars().all()
        
        for user_bot in user_bots:
            if user_bot.bot_id not in active_clients:
                try:
                    import os
                    os.makedirs('sessions', exist_ok=True)
                    
                    from config.settings import TELETHON_API_ID, TELETHON_API_HASH
                    
                    client = TelegramClient(
                        f'sessions/user_bot_{user_bot.bot_id}',
                        api_id=TELETHON_API_ID,
                        api_hash=TELETHON_API_HASH
                    )
                    
                    await client.start(bot_token=user_bot.bot_token)
                    
                    client.add_event_handler(
                        lambda event: handle_new_channel_post(event, user_bot.user_id),
                        events.NewMessage(chats=None)
                    )
                    
                    active_clients[user_bot.bot_id] = client
                    
                except Exception as e:
                    print(f"Error starting bot {user_bot.bot_id}: {e}")


async def handle_new_channel_post(event, user_id):
    if not event.message.post:
        return
    
    try:
        async with await get_session() as session:
            query_sub = select(Subscription).where(
                and_(
                    Subscription.user_id == user_id,
                    Subscription.is_active == True,
                    Subscription.end_date > datetime.utcnow()
                )
            )
            result_sub = await session.execute(query_sub)
            subscription = result_sub.scalar_one_or_none()
            
            if not subscription:
                return
            
            query_channel = select(Channel).where(
                and_(
                    Channel.user_id == user_id,
                    Channel.channel_tg_id == event.chat_id
                )
            )
            result_channel = await session.execute(query_channel)
            channel = result_channel.scalar_one_or_none()
            
            if not channel:
                return
            
            query_settings = select(ReactionsSettings).where(
                and_(
                    ReactionsSettings.user_id == user_id,
                    ReactionsSettings.channel_id == channel.channel_id,
                    ReactionsSettings.is_active == True
                )
            )
            result_settings = await session.execute(query_settings)
            settings = result_settings.scalar_one_or_none()
            
            if not settings:
                return
            
            if subscription.tariff:
                parts = subscription.tariff.split('/')
                if len(parts) == 2:
                    reactions_count = int(parts[1])
                else:
                    reactions_count = 5
            else:
                reactions_count = 5
            
            asyncio.create_task(
                add_reactions_to_post(
                    event.client,
                    event.chat_id,
                    event.message.id,
                    settings.reaction_pool,
                    reactions_count,
                    settings.interval_minutes
                )
            )
            
    except Exception as e:
        print(f"Error handling new post: {e}")


async def add_reactions_to_post(client, chat_id, message_id, reaction_pool, count, interval_minutes):
    try:
        for i in range(count):
            if i > 0:
                delay = random.randint(interval_minutes * 60, (interval_minutes + 2) * 60)
                await asyncio.sleep(delay)
            
            reaction = random.choice(reaction_pool)
            
            await client(SendReactionRequest(
                peer=chat_id,
                msg_id=message_id,
                reaction=[ReactionEmoji(emoticon=reaction)]
            ))
            
            await asyncio.sleep(random.randint(2, 5))
            
    except Exception as e:
        print(f"Error adding reaction: {e}")