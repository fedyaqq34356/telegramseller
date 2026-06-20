from functools import wraps
from aiogram.types import Message, CallbackQuery
from config.settings import ADMIN_IDS


def admin_only(func):
    @wraps(func)
    async def wrapper(event, *args, **kwargs):
        user_id = None
        
        if isinstance(event, Message):
            user_id = event.from_user.id
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id
        
        if user_id not in ADMIN_IDS:
            if isinstance(event, Message):
                await event.answer("❌ У вас нет прав администратора")
            elif isinstance(event, CallbackQuery):
                await event.answer("❌ У вас нет прав администратора", show_alert=True)
            return
        
        return await func(event, *args, **kwargs)
    
    return wrapper