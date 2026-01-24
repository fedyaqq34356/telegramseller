from telethon import TelegramClient


async def view_post(client: TelegramClient, channel_id: int, message_id: int):
    try:
        await client.get_messages(channel_id, ids=message_id)
        return True
    except Exception as e:
        print(f"Error viewing post: {e}")
        return False


async def view_multiple_posts(client: TelegramClient, channel_id: int, message_ids: list):
    success_count = 0
    
    for message_id in message_ids:
        if await view_post(client, channel_id, message_id):
            success_count += 1
    
    return success_count


async def get_post_views(client: TelegramClient, channel_id: int, message_id: int):
    try:
        message = await client.get_messages(channel_id, ids=message_id)
        if message and hasattr(message, 'views'):
            return message.views
        return 0
    except Exception as e:
        print(f"Error getting post views: {e}")
        return 0