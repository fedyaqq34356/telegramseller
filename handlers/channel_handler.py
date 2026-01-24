from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy import select

from models.user import User
from models.channel import Channel, ReactionsSettings
from config.database import get_session
from config.settings import AVAILABLE_REACTIONS, DEFAULT_REACTION_INTERVAL
from utils.keyboards import get_back_button
from utils.messages import get_message
from services.channel_service import get_user_channels

router = Router()


class ChannelStates(StatesGroup):
    selecting_reactions = State()
    setting_interval = State()


@router.callback_query(F.data == 'manage_channels')
async def manage_channels_menu(callback: CallbackQuery):
    user_id = callback.from_user.id
    
    async with await get_session() as session:
        query_user = select(User).where(User.user_id == user_id)
        result_user = await session.execute(query_user)
        user = result_user.scalar_one_or_none()
        
        if not user:
            return
        
        lang = user.language
        channels = await get_user_channels(user_id)
        
        if not channels:
            await callback.message.edit_text(
                get_message(lang, 'no_channels'),
                reply_markup=get_back_button(lang)
            )
        else:
            text = "📺 Ваши каналы:\n\n" if lang == 'ru' else "📺 Your channels:\n\n"
            for ch in channels:
                text += f"• {ch.channel_title} (@{ch.channel_username})\n"
            
            await callback.message.edit_text(
                text,
                reply_markup=get_back_button(lang)
            )
    
    await callback.answer()


@router.callback_query(F.data.startswith('edit_reactions_'))
async def edit_reactions(callback: CallbackQuery, state: FSMContext):
    channel_id = int(callback.data.split('_')[2])
    user_id = callback.from_user.id
    
    async with await get_session() as session:
        query = select(ReactionsSettings).where(
            ReactionsSettings.channel_id == channel_id,
            ReactionsSettings.user_id == user_id
        )
        result = await session.execute(query)
        settings = result.scalar_one_or_none()
        
        if settings:
            await state.update_data(channel_id=channel_id, settings_id=settings.settings_id)
            
            query_user = select(User).where(User.user_id == user_id)
            result_user = await session.execute(query_user)
            user = result_user.scalar_one_or_none()
            
            if user:
                lang = user.language
                from utils.keyboards import get_reactions_keyboard
                await callback.message.edit_text(
                    get_message(lang, 'select_reactions'),
                    reply_markup=get_reactions_keyboard(selected=settings.reaction_pool, lang=lang)
                )
                await state.set_state(ChannelStates.selecting_reactions)
    
    await callback.answer()