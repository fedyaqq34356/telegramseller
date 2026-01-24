from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from utils.decorators import admin_only
from utils.keyboards import get_admin_menu_keyboard

router = Router()


@router.message(Command('admin'))
@admin_only
async def admin_panel(message: Message):
    await message.answer(
        "🔧 Админ-панель\n\nВыберите действие:",
        reply_markup=get_admin_menu_keyboard()
    )