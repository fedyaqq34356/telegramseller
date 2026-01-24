from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy import select, func, and_
from datetime import datetime, timedelta

from models.user import User
from models.subscription import Subscription
from models.payment import Payment
from config.database import get_session
from utils.decorators import admin_only
from utils.keyboards import get_admin_menu_keyboard

router = Router()


@router.callback_query(F.data == 'admin_stats')
@admin_only
async def admin_statistics(callback: CallbackQuery):
    async with await get_session() as session:
        total_users_q = select(func.count(User.user_id))
        total_users = await session.scalar(total_users_q)
        
        today = datetime.utcnow().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        today_users_q = select(func.count(User.user_id)).where(
            func.date(User.registration_date) == today
        )
        today_users = await session.scalar(today_users_q) or 0
        
        week_users_q = select(func.count(User.user_id)).where(
            func.date(User.registration_date) >= week_ago
        )
        week_users = await session.scalar(week_users_q) or 0
        
        month_users_q = select(func.count(User.user_id)).where(
            func.date(User.registration_date) >= month_ago
        )
        month_users = await session.scalar(month_users_q) or 0
        
        ru_users_q = select(func.count(User.user_id)).where(User.system_language == 'ru')
        ru_users = await session.scalar(ru_users_q) or 0
        
        ua_users_q = select(func.count(User.user_id)).where(User.system_language == 'uk')
        ua_users = await session.scalar(ua_users_q) or 0
        
        en_users_q = select(func.count(User.user_id)).where(User.system_language == 'en')
        en_users = await session.scalar(en_users_q) or 0
        
        other_users = total_users - ru_users - ua_users - en_users
        
        demo_subs_q = select(func.count(Subscription.subscription_id)).where(
            Subscription.subscription_type == 'demo'
        )
        demo_subs = await session.scalar(demo_subs_q) or 0
        
        paid_subs_q = select(func.count(Subscription.subscription_id)).where(
            and_(
                Subscription.subscription_type != 'demo',
                Subscription.is_active == True,
                Subscription.end_date > datetime.utcnow()
            )
        )
        paid_subs = await session.scalar(paid_subs_q) or 0
        
        crypto_payments_q = select(func.count(func.distinct(Payment.user_id))).where(
            and_(
                Payment.payment_method == 'crypto',
                Payment.status == 'confirmed'
            )
        )
        crypto_users = await session.scalar(crypto_payments_q) or 0
        
        stars_payments_q = select(func.count(func.distinct(Payment.user_id))).where(
            and_(
                Payment.payment_method == 'stars',
                Payment.status == 'confirmed'
            )
        )
        stars_users = await session.scalar(stars_payments_q) or 0
        
        crypto_income_q = select(func.sum(Payment.amount)).where(
            and_(
                Payment.payment_method == 'crypto',
                Payment.status == 'confirmed'
            )
        )
        crypto_income = await session.scalar(crypto_income_q) or 0
        
        stars_income_q = select(func.sum(Payment.amount)).where(
            and_(
                Payment.payment_method == 'stars',
                Payment.status == 'confirmed'
            )
        )
        stars_income = await session.scalar(stars_income_q) or 0
        
        stats_text = f"""📊 Статистика бота

👥 Пользователи:
Всего: {total_users}
Новых сегодня: {today_users}
Новых за неделю: {week_users}
Новых за месяц: {month_users}

🌍 По языкам:
🇷🇺 RU: {ru_users}
🇬🇧 EN: {en_users}
Другие: {other_users}

💎 Подписки:
Демо активировано: {demo_subs}
Платных активно: {paid_subs}

💰 Оплаты:
Оплата криптой: {crypto_users} пользователей
Оплата звездами: {stars_users} пользователей

💵 Доход:
Крипто: ${crypto_income:.2f}
Stars: {int(stars_income)} ⭐"""
        
        await callback.message.edit_text(
            stats_text,
            reply_markup=get_admin_menu_keyboard()
        )
    
    await callback.answer()