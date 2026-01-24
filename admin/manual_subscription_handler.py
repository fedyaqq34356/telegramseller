from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy import select

from models.user import User
from models.subscription import Tariff
from config.database import get_session
from utils.decorators import admin_only
from services.subscription_service import create_subscription

router = Router()


class ManualSubStates(StatesGroup):
    waiting_user_id = State()
    selecting_type = State()
    selecting_period = State()
    selecting_tariff = State()


@router.callback_query(F.data == 'admin_give_sub')
@admin_only
async def give_subscription_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "👤 Введите Telegram ID пользователя:"
    )
    await state.set_state(ManualSubStates.waiting_user_id)
    await callback.answer()


@router.message(ManualSubStates.waiting_user_id)
@admin_only
async def process_user_id(message: Message, state: FSMContext):
    try:
        user_id = int(message.text.strip())
        
        async with await get_session() as session:
            query = select(User).where(User.user_id == user_id)
            result = await session.execute(query)
            user = result.scalar_one_or_none()
            
            if not user:
                await message.answer("❌ Пользователь не найден")
                return
            
            await state.update_data(target_user_id=user_id)
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🎯 Реакции", callback_data="manual_sub_reactions")],
                [InlineKeyboardButton(text="🎬 Кружки", callback_data="manual_sub_circles")],
                [InlineKeyboardButton(text="📤 Постинг", callback_data="manual_sub_posting")],
                [InlineKeyboardButton(text="👑 Премиум", callback_data="manual_sub_premium")]
            ])
            
            await message.answer(
                f"✅ Пользователь найден\n\nID: {user_id}\nUsername: @{user.username}\n\nВыберите тип подписки:",
                reply_markup=keyboard
            )
            
            await state.set_state(ManualSubStates.selecting_type)
            
    except ValueError:
        await message.answer("❌ Введите корректный ID")


@router.callback_query(F.data.startswith('manual_sub_'), ManualSubStates.selecting_type)
@admin_only
async def select_sub_type(callback: CallbackQuery, state: FSMContext):
    sub_type = callback.data.replace('manual_sub_', '')
    await state.update_data(subscription_type=sub_type)
    
    if sub_type == 'reactions':
        async with await get_session() as session:
            query = select(Tariff)
            result = await session.execute(query)
            tariffs = result.scalars().all()
            
            if tariffs:
                buttons = []
                for tariff in tariffs:
                    buttons.append([InlineKeyboardButton(
                        text=f"{tariff.views_count}/{tariff.reactions_count}",
                        callback_data=f"manual_tariff_{tariff.tariff_id}"
                    )])
                
                keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
                
                await callback.message.edit_text(
                    "Выберите тариф:",
                    reply_markup=keyboard
                )
                
                await state.set_state(ManualSubStates.selecting_tariff)
            else:
                await callback.message.edit_text("❌ Тарифы не настроены")
    else:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="1 месяц", callback_data="manual_period_1")],
            [InlineKeyboardButton(text="3 месяца", callback_data="manual_period_3")],
            [InlineKeyboardButton(text="6 месяцев", callback_data="manual_period_6")],
            [InlineKeyboardButton(text="12 месяцев", callback_data="manual_period_12")]
        ])
        
        await callback.message.edit_text(
            "Выберите период:",
            reply_markup=keyboard
        )
        
        await state.set_state(ManualSubStates.selecting_period)
    
    await callback.answer()


@router.callback_query(F.data.startswith('manual_tariff_'), ManualSubStates.selecting_tariff)
@admin_only
async def select_tariff(callback: CallbackQuery, state: FSMContext):
    tariff_id = int(callback.data.split('_')[2])
    
    async with await get_session() as session:
        query = select(Tariff).where(Tariff.tariff_id == tariff_id)
        result = await session.execute(query)
        tariff = result.scalar_one_or_none()
        
        if tariff:
            await state.update_data(tariff_name=tariff.name)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="1 месяц", callback_data="manual_period_1")],
        [InlineKeyboardButton(text="3 месяца", callback_data="manual_period_3")],
        [InlineKeyboardButton(text="6 месяцев", callback_data="manual_period_6")],
        [InlineKeyboardButton(text="12 месяцев", callback_data="manual_period_12")]
    ])
    
    await callback.message.edit_text(
        "Выберите период:",
        reply_markup=keyboard
    )
    
    await state.set_state(ManualSubStates.selecting_period)
    await callback.answer()


@router.callback_query(F.data.startswith('manual_period_'), ManualSubStates.selecting_period)
@admin_only
async def select_period(callback: CallbackQuery, state: FSMContext):
    period = int(callback.data.split('_')[2])
    data = await state.get_data()
    
    target_user_id = data.get('target_user_id')
    subscription_type = data.get('subscription_type')
    tariff_name = data.get('tariff_name')
    
    await create_subscription(
        user_id=target_user_id,
        subscription_type=subscription_type,
        period_months=period,
        tariff=tariff_name
    )
    
    from main import bot
    try:
        await bot.send_message(
            target_user_id,
            f"🎉 Вам выдана подписка!\n\nТип: {subscription_type}\nПериод: {period} мес."
        )
    except:
        pass
    
    await callback.message.edit_text(
        f"✅ Подписка успешно выдана!\n\nПользователь: {target_user_id}\nТип: {subscription_type}\nПериод: {period} мес."
    )
    
    await state.clear()
    await callback.answer()