from aiogram import Router, F
from aiogram.types import CallbackQuery, FSInputFile
from sqlalchemy import select, and_
from datetime import datetime
import os

from models.user import User
from models.subscription import Subscription
from config.database import get_session
from utils.decorators import admin_only

router = Router()


@router.callback_query(F.data == 'admin_export')
@admin_only
async def export_users(callback: CallbackQuery):
    await callback.answer("⏳ Формируем файл...")
    
    async with await get_session() as session:
        query = select(User)
        result = await session.execute(query)
        users = result.scalars().all()
        
        filename = f'users_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
        filepath = f'media/temp/{filename}'
        
        os.makedirs('media/temp', exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"Экспорт пользователей - {datetime.now().strftime('%d.%m.%Y %H:%M')}\n")
            f.write("="*60 + "\n\n")
            
            for user in users:
                sub_query = select(Subscription).where(
                    and_(
                        Subscription.user_id == user.user_id,
                        Subscription.is_active == True,
                        Subscription.end_date > datetime.utcnow()
                    )
                )
                sub_result = await session.execute(sub_query)
                has_sub = sub_result.scalar_one_or_none() is not None
                
                f.write(f"ID: {user.user_id}\n")
                f.write(f"Username: @{user.username if user.username else 'нет'}\n")
                f.write(f"Имя: {user.first_name if user.first_name else 'нет'}\n")
                f.write(f"Подписка: {'✅' if has_sub else '❌'}\n")
                f.write(f"Заработано: ${user.total_earned:.2f}\n")
                f.write(f"Регистрация: {user.registration_date.strftime('%d.%m.%Y')}\n")
                f.write("-"*60 + "\n")
        
        from main import bot
        file = FSInputFile(filepath)
        await bot.send_document(
            chat_id=callback.from_user.id,
            document=file,
            caption=f"📥 Экспорт пользователей\n\nВсего: {len(users)}"
        )
        
        os.remove(filepath)
    
    await callback.answer()