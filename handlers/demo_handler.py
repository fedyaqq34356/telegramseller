from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy import select
from datetime import datetime, timedelta

from models.user import User
from models.channel import ReactionsSettings
from config.database import get_session
from config.settings import AVAILABLE_REACTIONS, DEMO_DAYS
from utils.keyboards import get_demo_options_keyboard, get_back_button
from utils.messages import get_message
from services.user_bot_service import validate_bot_token, save_user_bot
from services.channel_service import add_channel
from services.subscription_service import create_subscription

router = Router()


class DemoStates(StatesGroup):
    waiting_for_bot_token = State()
    waiting_for_channel = State()


@router.callback_query(F.data == 'demo_access')
async def demo_access_menu(callback: CallbackQuery):
    user_id = callback.from_user.id
    
    async with await get_session() as session:
        query = select(User).where(User.user_id == user_id)
        result = await session.execute(query)
        user = result.scalar_one_or_none()
        
        if not user:
            await callback.answer("Ошибка: пользователь не найден", show_alert=True)
            return
        
        lang = user.language
        
        if user.demo_used:
            await callback.message.edit_text(
                get_message(lang, 'demo_already_used'),
                reply_markup=get_back_button(lang)
            )
            await callback.answer()
            return
        
        await callback.message.edit_text(
            get_message(lang, 'demo_info'),
            reply_markup=get_demo_options_keyboard(lang)
        )
    
    await callback.answer()


@router.callback_query(F.data == 'demo_main_bot')
async def demo_main_bot(callback: CallbackQuery):
    user_id = callback.from_user.id
    
    async with await get_session() as session:
        query = select(User).where(User.user_id == user_id)
        result = await session.execute(query)
        user = result.scalar_one_or_none()
        
        if user:
            lang = user.language
            
            await callback.message.edit_text(
                get_message(lang, 'demo_main_bot_instruction'),
                reply_markup=get_back_button(lang)
            )
    
    await callback.answer()


@router.callback_query(F.data == 'demo_own_bot')
async def demo_own_bot(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    
    async with await get_session() as session:
        query = select(User).where(User.user_id == user_id)
        result = await session.execute(query)
        user = result.scalar_one_or_none()
        
        if user:
            lang = user.language
            
            await callback.message.edit_text(
                get_message(lang, 'demo_own_bot_instruction'),
                reply_markup=get_back_button(lang)
            )
            
            await callback.message.answer(
                get_message(lang, 'send_bot_token')
            )
            
            await state.set_state(DemoStates.waiting_for_bot_token)
    
    await callback.answer()


@router.message(DemoStates.waiting_for_bot_token)
async def process_bot_token(message: Message, state: FSMContext):
    token = message.text.strip()
    user_id = message.from_user.id
    
    async with await get_session() as session:
        query = select(User).where(User.user_id == user_id)
        result = await session.execute(query)
        user = result.scalar_one_or_none()
        
        if not user:
            return
        
        lang = user.language
        
        bot_info = await validate_bot_token(token)
        
        if not bot_info['valid']:
            await message.answer(
                get_message(lang, 'invalid_token'),
                reply_markup=get_back_button(lang)
            )
            return
        
        await save_user_bot(user_id, token, bot_info['username'])
        
        await message.answer(
            get_message(lang, 'bot_token_saved'),
            reply_markup=get_back_button(lang)
        )
        
        await state.clear()



@router.my_chat_member()
async def bot_added_to_channel(event, state: FSMContext):
    from aiogram.types import ChatMemberUpdated
    
    if not isinstance(event, ChatMemberUpdated):
        return
    

    if event.new_chat_member.status not in ['administrator', 'creator']:
        return
    
    chat = event.chat
    user_id = event.from_user.id
    
    if chat.type != 'channel':
        return
    
    async with await get_session() as session:
        query = select(User).where(User.user_id == user_id)
        result = await session.execute(query)
        user = result.scalar_one_or_none()
        
        if not user or user.demo_used:
            return
        
        lang = user.language
        

        channel = await add_channel(
            user_id=user_id,
            channel_username=chat.username or '',
            channel_title=chat.title,
            channel_tg_id=chat.id
        )
        
        await create_subscription(
            user_id=user_id,
            subscription_type='demo',
            period_months=0,
            tariff='5/5'
        )
        
        reactions_settings = ReactionsSettings(
            user_id=user_id,
            channel_id=channel.channel_id,
            reaction_pool=AVAILABLE_REACTIONS[:3], 
            interval_minutes=5,
            is_active=True
        )
        session.add(reactions_settings)
        
        # Помечаем демо как использованный
        user.demo_used = True
        
        query_sub = select(Subscription).where(
            Subscription.user_id == user_id,
            Subscription.subscription_type == 'demo'
        )
        result_sub = await session.execute(query_sub)
        subscription = result_sub.scalar_one_or_none()
        
        if subscription:
            subscription.end_date = datetime.utcnow() + timedelta(days=DEMO_DAYS)
        
        await session.commit()
        
        from bot import bot
        await bot.send_message(
            user_id,
            get_message(lang, 'demo_activated')
        )