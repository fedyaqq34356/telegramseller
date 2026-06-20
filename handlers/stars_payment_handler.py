from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, LabeledPrice
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy import select

from models.user import User
from models.payment import Payment
from config.database import get_session
from config.settings import STARS_CHANNEL_LINK
from utils.keyboards import get_stars_payment_keyboard, get_check_payment_keyboard, get_back_button
from utils.messages import get_message
from services.subscription_service import create_subscription

router = Router()


class StarsPaymentStates(StatesGroup):
    waiting_payment = State()


@router.callback_query(F.data == 'payment_stars', SubscriptionStates.selecting_payment)
async def select_stars_payment(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    data = await state.get_data()
    price = data.get('price', 0)
    
    #convert_to_stars_1usd_100stars
    stars_amount = int(price * 100)
    
    async with await get_session() as session:
        query = select(User).where(User.user_id == user_id)
        result = await session.execute(query)
        user = result.scalar_one_or_none()
        
        if user:
            lang = user.language
            subscription_type = data.get('subscription_type')
            period = data.get('period')
            
            #create_payment_record
            payment = Payment(
                user_id=user_id,
                amount=stars_amount,
                currency='XTR',
                payment_method='stars',
                subscription_type=subscription_type,
                subscription_period=period,
                tariff=data.get('tariff_name'),
                status='pending'
            )
            session.add(payment)
            await session.commit()
            await session.refresh(payment)
            
            await state.update_data(payment_id=payment.payment_id, stars_amount=stars_amount)
            
            #send_invoice
            prices = [LabeledPrice(label="XTR", amount=stars_amount)]
            
            await callback.message.answer_invoice(
                title=f"Подписка {subscription_type}",
                description=f"Подписка на {period} месяц(ев)",
                prices=prices,
                provider_token="",
                payload=f"{user_id}_{subscription_type}_{period}_{payment.payment_id}",
                currency="XTR",
                reply_markup=get_stars_payment_keyboard(stars_amount, lang)
            )
            
            await state.set_state(StarsPaymentStates.waiting_payment)
    
    await callback.answer()


@router.message(F.successful_payment)
async def successful_stars_payment(message: Message, state: FSMContext):
    user_id = message.from_user.id
    payment_info = message.successful_payment
    
    #parse_payload
    payload_parts = payment_info.invoice_payload.split('_')
    if len(payload_parts) >= 4:
        payment_id = int(payload_parts[3])
        
        async with await get_session() as session:
            query_payment = select(Payment).where(Payment.payment_id == payment_id)
            result_payment = await session.execute(query_payment)
            payment = result_payment.scalar_one_or_none()
            
            query_user = select(User).where(User.user_id == user_id)
            result_user = await session.execute(query_user)
            user = result_user.scalar_one_or_none()
            
            if payment and user:
                lang = user.language
                
                #update_payment
                payment.status = 'confirmed'
                payment.transaction_hash = payment_info.telegram_payment_charge_id
                
                #create_subscription
                await create_subscription(
                    user_id=user_id,
                    subscription_type=payment.subscription_type,
                    period_months=payment.subscription_period,
                    tariff=payment.tariff
                )
                
                #update_earnings
                user.total_earned += payment.amount / 100
                
                await session.commit()
                
                await message.answer(
                    get_message(
                        lang,
                        'payment_success',
                        type=payment.subscription_type,
                        period=payment.subscription_period
                    )
                )
                
                await state.clear()
                
                #notify_admin
                from config.settings import ADMIN_IDS
                from bot import bot
                for admin_id in ADMIN_IDS:
                    await bot.send_message(
                        admin_id,
                        f"⭐ Новая оплата Stars!\n\nUser ID: {user_id}\nUsername: @{user.username}\nСумма: {payment.amount} Stars\nПодписка: {payment.subscription_type} на {payment.subscription_period} мес."
                    )


@router.callback_query(F.data == 'check_payment_stars', StarsPaymentStates.waiting_payment)
async def check_stars_payment_callback(callback: CallbackQuery, state: FSMContext):
    await callback.answer("Пожалуйста, используйте кнопку оплаты выше", show_alert=True)