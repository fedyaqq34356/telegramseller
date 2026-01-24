from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy import select

from models.user import User
from models.subscription import Tariff
from config.database import get_session
from utils.keyboards import (
    get_subscription_types_keyboard,
    get_tariffs_keyboard,
    get_reactions_keyboard,
    get_period_keyboard,
    get_payment_methods_keyboard,
    get_back_button
)
from utils.messages import get_message

router = Router()


class SubscriptionStates(StatesGroup):
    selecting_type = State()
    selecting_tariff = State()
    selecting_reactions = State()
    selecting_period = State()
    selecting_payment = State()


@router.callback_query(F.data == 'buy_subscription')
async def buy_subscription_menu(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    
    async with await get_session() as session:
        query = select(User).where(User.user_id == user_id)
        result = await session.execute(query)
        user = result.scalar_one_or_none()
        
        if user:
            lang = user.language
            
            await callback.message.edit_text(
                get_message(lang, 'subscription_types'),
                reply_markup=get_subscription_types_keyboard(lang)
            )
            
            await state.set_state(SubscriptionStates.selecting_type)
    
    await callback.answer()


@router.callback_query(F.data == 'back_to_sub_types')
async def back_to_sub_types(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    
    async with await get_session() as session:
        query = select(User).where(User.user_id == user_id)
        result = await session.execute(query)
        user = result.scalar_one_or_none()
        
        if user:
            lang = user.language
            
            await callback.message.edit_text(
                get_message(lang, 'subscription_types'),
                reply_markup=get_subscription_types_keyboard(lang)
            )
            
            await state.set_state(SubscriptionStates.selecting_type)
    
    await callback.answer()


@router.callback_query(F.data == 'sub_type_reactions', SubscriptionStates.selecting_type)
async def select_reactions_type(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    
    await state.update_data(subscription_type='reactions')
    
    async with await get_session() as session:
        query_user = select(User).where(User.user_id == user_id)
        result_user = await session.execute(query_user)
        user = result_user.scalar_one_or_none()
        
        query_tariffs = select(Tariff)
        result_tariffs = await session.execute(query_tariffs)
        tariffs = result_tariffs.scalars().all()
        
        if user and tariffs:
            lang = user.language
            
            await callback.message.edit_text(
                get_message(lang, 'select_tariff'),
                reply_markup=get_tariffs_keyboard(tariffs, lang)
            )
            
            await state.set_state(SubscriptionStates.selecting_tariff)
    
    await callback.answer()


@router.callback_query(F.data.startswith('tariff_'), SubscriptionStates.selecting_tariff)
async def select_tariff(callback: CallbackQuery, state: FSMContext):
    tariff_id = int(callback.data.split('_')[1])
    user_id = callback.from_user.id
    
    async with await get_session() as session:
        query_tariff = select(Tariff).where(Tariff.tariff_id == tariff_id)
        result_tariff = await session.execute(query_tariff)
        tariff = result_tariff.scalar_one_or_none()
        
        query_user = select(User).where(User.user_id == user_id)
        result_user = await session.execute(query_user)
        user = result_user.scalar_one_or_none()
        
        if tariff and user:
            await state.update_data(tariff_id=tariff_id, tariff_name=tariff.name)
            lang = user.language
            
            await callback.message.edit_text(
                get_message(lang, 'select_reactions'),
                reply_markup=get_reactions_keyboard(selected=[], lang=lang)
            )
            
            await state.set_state(SubscriptionStates.selecting_reactions)
    
    await callback.answer()


@router.callback_query(F.data.startswith('reaction_'), SubscriptionStates.selecting_reactions)
async def toggle_reaction(callback: CallbackQuery, state: FSMContext):
    reaction = callback.data.split('_')[1]
    user_id = callback.from_user.id
    
    data = await state.get_data()
    selected = data.get('selected_reactions', [])
    
    if reaction in selected:
        selected.remove(reaction)
    else:
        selected.append(reaction)
    
    await state.update_data(selected_reactions=selected)
    
    async with await get_session() as session:
        query = select(User).where(User.user_id == user_id)
        result = await session.execute(query)
        user = result.scalar_one_or_none()
        
        if user:
            lang = user.language
            
            await callback.message.edit_reply_markup(
                reply_markup=get_reactions_keyboard(selected=selected, lang=lang)
            )
    
    await callback.answer()


@router.callback_query(F.data == 'reactions_done', SubscriptionStates.selecting_reactions)
async def reactions_done(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    data = await state.get_data()
    selected = data.get('selected_reactions', [])
    
    if not selected:
        await callback.answer("Выберите хотя бы одну реакцию", show_alert=True)
        return
    
    tariff_id = data.get('tariff_id')
    
    async with await get_session() as session:
        query_tariff = select(Tariff).where(Tariff.tariff_id == tariff_id)
        result_tariff = await session.execute(query_tariff)
        tariff = result_tariff.scalar_one_or_none()
        
        query_user = select(User).where(User.user_id == user_id)
        result_user = await session.execute(query_user)
        user = result_user.scalar_one_or_none()
        
        if tariff and user:
            lang = user.language
            
            prices = {
                '1m': tariff.price_1m,
                '3m': tariff.price_3m,
                '6m': tariff.price_6m,
                '12m': tariff.price_12m
            }
            
            await callback.message.edit_text(
                get_message(lang, 'select_period'),
                reply_markup=get_period_keyboard(prices, lang)
            )
            
            await state.set_state(SubscriptionStates.selecting_period)
    
    await callback.answer()


@router.callback_query(F.data.startswith('period_'), SubscriptionStates.selecting_period)
async def select_period(callback: CallbackQuery, state: FSMContext):
    period = int(callback.data.split('_')[1])
    user_id = callback.from_user.id
    
    data = await state.get_data()
    tariff_id = data.get('tariff_id')
    
    async with await get_session() as session:
        query_tariff = select(Tariff).where(Tariff.tariff_id == tariff_id)
        result_tariff = await session.execute(query_tariff)
        tariff = result_tariff.scalar_one_or_none()
        
        query_user = select(User).where(User.user_id == user_id)
        result_user = await session.execute(query_user)
        user = result_user.scalar_one_or_none()
        
        if tariff and user:
            lang = user.language
            
            #calculate_price
            price_key = f'price_{period}m'
            price = getattr(tariff, price_key, 0)
            
            await state.update_data(period=period, price=price)
            
            await callback.message.edit_text(
                get_message(lang, 'payment_method'),
                reply_markup=get_payment_methods_keyboard(lang)
            )
            
            await state.set_state(SubscriptionStates.selecting_payment)
    
    await callback.answer()


@router.callback_query(F.data == 'sub_type_circles', SubscriptionStates.selecting_type)
async def select_circles_type(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    
    await state.update_data(subscription_type='circles')
    
    async with await get_session() as session:
        query = select(User).where(User.user_id == user_id)
        result = await session.execute(query)
        user = result.scalar_one_or_none()
        
        if user:
            lang = user.language
            
            from utils.helpers import get_admin_setting
            price_str = await get_admin_setting('circles_price', '500')
            
            try:
                price = float(price_str)
            except:
                price = 500.0
            
            prices = {
                '1m': price,
                '3m': price * 3 * 0.9,
                '6m': price * 6 * 0.85,
                '12m': price * 12 * 0.8
            }
            
            await callback.message.edit_text(
                get_message(lang, 'select_period'),
                reply_markup=get_period_keyboard(prices, lang)
            )
            
            await state.set_state(SubscriptionStates.selecting_period)
    
    await callback.answer()


@router.callback_query(F.data == 'sub_type_posting', SubscriptionStates.selecting_type)
async def select_posting_type(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    
    await state.update_data(subscription_type='posting')
    
    async with await get_session() as session:
        query = select(User).where(User.user_id == user_id)
        result = await session.execute(query)
        user = result.scalar_one_or_none()
        
        if user:
            lang = user.language
            
            from utils.helpers import get_admin_setting
            price_str = await get_admin_setting('posting_price', '700')
            
            try:
                price = float(price_str)
            except:
                price = 700.0
            
            prices = {
                '1m': price,
                '3m': price * 3 * 0.9,
                '6m': price * 6 * 0.85,
                '12m': price * 12 * 0.8
            }
            
            await callback.message.edit_text(
                get_message(lang, 'select_period'),
                reply_markup=get_period_keyboard(prices, lang)
            )
            
            await state.set_state(SubscriptionStates.selecting_period)
    
    await callback.answer()


@router.callback_query(F.data == 'sub_type_premium', SubscriptionStates.selecting_type)
async def select_premium_type(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    
    await state.update_data(subscription_type='premium')
    
    async with await get_session() as session:
        query = select(User).where(User.user_id == user_id)
        result = await session.execute(query)
        user = result.scalar_one_or_none()