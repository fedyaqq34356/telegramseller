from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy import select

from models.user import User
from config.database import get_session
from utils.keyboards import get_back_button
from utils.messages import get_message
from utils.helpers import format_datetime
from services.subscription_service import get_user_subscriptions
from services.channel_service import get_user_channels

router = Router()


@router.callback_query(F.data == 'my_settings')
async def my_settings_menu(callback: CallbackQuery):
    user_id = callback.from_user.id
    
    async with await get_session() as session:
        query = select(User).where(User.user_id == user_id)
        result = await session.execute(query)
        user = result.scalar_one_or_none()
        
        if not user:
            return
        
        lang = user.language
        
        #get_subscriptions
        subscriptions = await get_user_subscriptions(user_id)
        
        if subscriptions:
            subs_text = '\n'.join([
                f"• {sub.subscription_type} до {format_datetime(sub.end_date)}"
                for sub in subscriptions
            ])
        else:
            subs_text = get_message(lang, 'no_active_subs')
        
        #get_channels
        channels = await get_user_channels(user_id)
        
        if channels:
            channels_text = '\n'.join([
                f"• {ch.channel_title} (@{ch.channel_username})"
                for ch in channels
            ])
        else:
            channels_text = get_message(lang, 'no_channels')
        
        settings_text = get_message(
            lang,
            'settings_info',
            user_id=user_id,
            date=format_datetime(user.registration_date),
            subscriptions=subs_text,
            channels=channels_text
        )
        
        await callback.message.edit_text(
            settings_text,
            reply_markup=get_back_button(lang)
        )
    
    await callback.answer()