from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy import select

from models.user import User
from config.database import get_session
from utils.keyboards import get_language_keyboard, get_main_menu_keyboard
from utils.messages import get_message
from utils.helpers import get_admin_setting

router = Router()


@router.message(CommandStart())
async def start_command(message: Message, state: FSMContext):
    user_id = message.from_user.id
    
    async with await get_session() as session:
        query = select(User).where(User.user_id == user_id)
        result = await session.execute(query)
        user = result.scalar_one_or_none()
        
        if not user:
            user = User(
                user_id=user_id,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                system_language=message.from_user.language_code or 'ru'
            )
            session.add(user)
            await session.commit()
            await message.answer(
                "👋 Выберите язык / Choose language:",
                reply_markup=get_language_keyboard()
            )
        else:
            lang = user.language
            
            welcome_msg = await get_admin_setting(f'welcome_message_{lang}')
            if not welcome_msg:
                welcome_msg = get_message(lang, 'welcome')
            
            await message.answer(
                welcome_msg,
                reply_markup=get_main_menu_keyboard(lang)
            )


@router.callback_query(F.data.startswith('lang_'))
async def language_selected(callback: CallbackQuery, state: FSMContext):
    lang = callback.data.split('_')[1]  # ru или en
    user_id = callback.from_user.id
    
    # Сохраняем выбранный язык
    async with await get_session() as session:
        query = select(User).where(User.user_id == user_id)
        result = await session.execute(query)
        user = result.scalar_one_or_none()
        
        if user:
            user.language = lang
            await session.commit()
    
    # Получаем приветственное сообщение
    welcome_msg = await get_admin_setting(f'welcome_message_{lang}')
    if not welcome_msg:
        welcome_msg = get_message(lang, 'welcome')
    
    await callback.message.edit_text(
        welcome_msg,
        reply_markup=get_main_menu_keyboard(lang)
    )
    await callback.answer()


@router.callback_query(F.data == 'back_to_menu')
async def back_to_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    
    user_id = callback.from_user.id
    
    async with await get_session() as session:
        query = select(User).where(User.user_id == user_id)
        result = await session.execute(query)
        user = result.scalar_one_or_none()
        
        if user:
            lang = user.language
            welcome_msg = await get_admin_setting(f'welcome_message_{lang}')
            if not welcome_msg:
                welcome_msg = get_message(lang, 'welcome')
            
            await callback.message.edit_text(
                welcome_msg,
                reply_markup=get_main_menu_keyboard(lang)
            )
    
    await callback.answer()