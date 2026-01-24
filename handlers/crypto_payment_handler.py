from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy import select

from models.user import User
from models.settings import CryptoWallet
from models.payment import Payment
from config.database import get_session
from utils.keyboards import get_crypto_currencies_keyboard, get_check_payment_keyboard, get_back_button
from utils.messages import get_message
from services.payment_service import crypto_pay
from services.subscription_service import create_subscription
from services.channel_service import add_channel
from models.channel import ReactionsSettings

router = Router()


class CryptoPaymentStates(StatesGroup):
    selecting_currency = State()
    waiting_payment = State()


@router.callback_query(F.data == 'payment_crypto', SubscriptionStates.selecting_payment)
async def select_crypto_payment(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    
    async with await get_session() as session:
        query_user = select(User).where(User.user_id == user_id)
        result_user = await session.execute(query_user)
        user = result_user.scalar_one_or_none()
        
        query_wallets = select(CryptoWallet).where(CryptoWallet.is_active == True)
        result_wallets = await session.execute(query_wallets)
        wallets = result_wallets.scalars().all()
        
        if user and wallets:
            lang = user.language
            
            await callback.message.edit_text(
                "💰 Выберите криптовалюту:" if lang == 'ru' else "💰 Select cryptocurrency:",
                reply_markup=get_crypto_currencies_keyboard(wallets)
            )
            
            await state.set_state(CryptoPaymentStates.selecting_currency)
    
    await callback.answer()


@router.callback_query(F.data.startswith('crypto_'), CryptoPaymentStates.selecting_currency)
async def process_crypto_payment(callback: CallbackQuery, state: FSMContext):
    wallet_id = int(callback.data.split('_')[1])
    user_id = callback.from_user.id
    
    data = await state.get_data()
    price = data.get('price', 0)
    subscription_type = data.get('subscription_type')
    period = data.get('period')
    
    async with await get_session() as session:
        query_wallet = select(CryptoWallet).where(CryptoWallet.wallet_id == wallet_id)
        result_wallet = await session.execute(query_wallet)
        wallet = result_wallet.scalar_one_or_none()
        
        query_user = select(User).where(User.user_id == user_id)
        result_user = await session.execute(query_user)
        user = result_user.scalar_one_or_none()
        
        if wallet and user:
            lang = user.language
            
            #create_invoice_via_cryptobot
            invoice = await crypto_pay.create_invoice(
                amount=price,
                asset=wallet.currency_name,
                description=f"Subscription {subscription_type} for {period} months",
                payload=f"{user_id}_{subscription_type}_{period}"
            )
            
            if invoice:
                #save_payment_to_db
                payment = Payment(
                    user_id=user_id,
                    amount=price,
                    currency=wallet.currency_name,
                    payment_method='crypto',
                    invoice_id=str(invoice['invoice_id']),
                    subscription_type=subscription_type,
                    subscription_period=period,
                    tariff=data.get('tariff_name'),
                    status='pending'
                )
                session.add(payment)
                await session.commit()
                
                await state.update_data(
                    invoice_id=invoice['invoice_id'],
                    payment_id=payment.payment_id
                )
                
                bot_invoice_url = invoice.get('bot_invoice_url', '')
                
                message_text = f"""💰 Оплата криптовалютой

💵 Сумма: {price} {wallet.currency_name}
🔗 Ссылка для оплаты: {bot_invoice_url}

После оплаты нажмите кнопку проверки."""

                await callback.message.edit_text(
                    message_text,
                    reply_markup=get_check_payment_keyboard(lang)
                )
                
                await state.set_state(CryptoPaymentStates.waiting_payment)
            else:
                await callback.answer("Ошибка создания платежа", show_alert=True)
    
    await callback.answer()


@router.callback_query(F.data == 'check_payment', CryptoPaymentStates.waiting_payment)
async def check_crypto_payment(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    data = await state.get_data()
    invoice_id = data.get('invoice_id')
    payment_id = data.get('payment_id')
    
    async with await get_session() as session:
        query_user = select(User).where(User.user_id == user_id)
        result_user = await session.execute(query_user)
        user = result_user.scalar_one_or_none()
        
        if not user:
            return
        
        lang = user.language
        
        #check_invoice_status
        is_paid = await crypto_pay.check_invoice_paid(invoice_id)
        
        if is_paid:
            #update_payment_status
            query_payment = select(Payment).where(Payment.payment_id == payment_id)
            result_payment = await session.execute(query_payment)
            payment = result_payment.scalar_one_or_none()
            
            if payment:
                payment.status = 'confirmed'
                
                subscription_type = data.get('subscription_type')
                period = data.get('period')
                tariff_name = data.get('tariff_name')
                
                #create_subscription
                await create_subscription(
                    user_id=user_id,
                    subscription_type=subscription_type,
                    period_months=period,
                    tariff=tariff_name
                )
                
                #update_total_earned
                user.total_earned += payment.amount
                
                await session.commit()
                
                await callback.message.edit_text(
                    get_message(lang, 'payment_success', type=subscription_type, period=period),
                    reply_markup=get_back_button(lang)
                )
                
                await state.clear()
                
                #notify_admin
                from config.settings import ADMIN_IDS
                from bot import bot
                for admin_id in ADMIN_IDS:
                    await bot.send_message(
                        admin_id,
                        f"💰 Новая оплата!\n\nUser ID: {user_id}\nUsername: @{user.username}\nСумма: {payment.amount} {payment.currency}\nПодписка: {subscription_type} на {period} мес."
                    )
        else:
            await callback.answer(
                get_message(lang, 'payment_not_found'),
                show_alert=True
            )
    
    await callback.answer()


@router.callback_query(F.data == 'back_to_payment')
async def back_to_payment(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    
    async with await get_session() as session:
        query = select(User).where(User.user_id == user_id)
        result = await session.execute(query)
        user = result.scalar_one_or_none()
        
        if user:
            lang = user.language
            
            await callback.message.edit_text(
                get_message(lang, 'payment_method'),
                reply_markup=get_payment_methods_keyboard(lang)
            )
            
            await state.set_state(SubscriptionStates.selecting_payment)
    
    await callback.answer()