import random
from telethon import TelegramClient
from telethon.tl.functions.messages import SendReactionRequest
from telethon.tl.types import ReactionEmoji


async def send_reaction(client: TelegramClient, chat_id: int, message_id: int, reaction: str):
    try:
        await client(SendReactionRequest(
            peer=chat_id,
            msg_id=message_id,
            reaction=[ReactionEmoji(emoticon=reaction)]
        ))
        return True
    except Exception as e:
        print(f"Error sending reaction: {e}")
        return False


async def send_multiple_reactions(client: TelegramClient, chat_id: int, message_id: int, reactions: list, count: int):
    success_count = 0
    
    for i in range(count):
        reaction = random.choice(reactions)
        
        if await send_reaction(client, chat_id, message_id, reaction):
            success_count += 1
    
    return success_count


async def get_channel_post(client: TelegramClient, channel_id: int, message_id: int):
    try:
        message = await client.get_messages(channel_id, ids=message_id)
        return message
    except Exception as e:
        print(f"Error getting channel post: {e}")
        return None