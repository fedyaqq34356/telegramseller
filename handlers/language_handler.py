from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy import select

from models.user import User
from config.database import get_session
from utils.keyboards import get_language_keyboard, get_main_menu_keyboard
from utils.messages import get_message
from utils.helpers import get_admin_setting

router = Router()


@router.callback_query(F.data == 'change_language')
async def change_language_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "👋 Выберите язык / Choose language:",
        reply_markup=get_language_keyboard()
    )
    await callback.answer()