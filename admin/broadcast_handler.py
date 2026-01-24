from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy import select, and_
from datetime import datetime
import asyncio

from models.user import User
from models.subscription import Subscription
from config.database import get_session
from utils.decorators import admin_only
from utils.keyboards import get_broadcast_filters_keyboard, get_admin_menu_keyboard
from utils.validators import parse_buttons

router = Router()


class BroadcastStates(StatesGroup):
    waiting_content = State()
    selecting_filters = State()


@router.callback_query(F.data == 'admin_broadcast')
@admin_only
async def broadcast_menu(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "📢 Рассылка\n\nВыберите аудиторию:",
        reply_markup=get_broadcast_filters_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == 'broadcast_all')
@admin_only
async def broadcast_all_users(callback: CallbackQuery, state: FSMContext):
    await state.update_data(filters={})
    
    await callback.message.edit_text(
        "📝 Отправьте сообщение для рассылки.\n\nМожете отправить:\n- Текст\n- Текст + Фото\n- Добавить кнопку: НАЗВАНИЕ | ССЫЛКА"
    )
    
    await state.set_state(BroadcastStates.waiting_content)
    await callback.answer()


@router.callback_query(F.data == 'broadcast_filters')
@admin_only
async def broadcast_with_filters(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "🎯 Функционал фильтров в разработке.\n\nИспользуйте рассылку всем пользователям."
    )
    await callback.answer()


@router.message(BroadcastStates.waiting_content)
@admin_only
async def process_broadcast_content(message: Message, state: FSMContext):
    data = await state.get_data()
    filters = data.get('filters', {})
    
    text = message.text or message.caption or ""
    photo = None
    
    if message.photo:
        photo = message.photo[-1].file_id
    
    buttons = []
    if text:
        lines = text.split('\n')
        clean_text = []
        for line in lines:
            if '|' in line and line.count('|') == 1:
                parsed = parse_buttons(line)
                if parsed:
                    buttons.extend(parsed)
                else:
                    clean_text.append(line)
            else:
                clean_text.append(line)
        text = '\n'.join(clean_text)
    
    async with await get_session() as session:
        query = select(User).where(User.is_blocked == False)
        result = await session.execute(query)
        users = result.scalars().all()
        
        success = 0
        failed = 0
        
        status_msg = await message.answer(f"🔄 Начинаем рассылку...\n\nВсего пользователей: {len(users)}")
        
        from main import bot
        
        for user in users:
            try:
                keyboard = None
                if buttons:
                    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
                    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text=btn['name'], url=btn['url'])]
                        for btn in buttons
                    ])
                
                if photo:
                    await bot.send_photo(
                        chat_id=user.user_id,
                        photo=photo,
                        caption=text,
                        reply_markup=keyboard
                    )
                else:
                    await bot.send_message(
                        chat_id=user.user_id,
                        text=text,
                        reply_markup=keyboard
                    )
                
                success += 1
                
                if success % 10 == 0:
                    await status_msg.edit_text(
                        f"🔄 Рассылка...\n\n✅ Успешно: {success}\n❌ Ошибок: {failed}"
                    )
                
                await asyncio.sleep(0.05)
                
            except Exception as e:
                failed += 1
                if 'blocked' in str(e).lower():
                    user.is_blocked = True
        
        await session.commit()
        
        await status_msg.edit_text(
            f"✅ Рассылка завершена!\n\n✅ Успешно: {success}\n❌ Ошибок: {failed}"
        )
    
    await state.clear()