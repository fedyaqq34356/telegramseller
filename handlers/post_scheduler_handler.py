from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy import select
import json

from models.user import User
from models.settings import PostQueue
from models.channel import Channel
from config.database import get_session
from config.settings import FREE_POSTS_PER_DAY
from utils.keyboards import get_back_button, get_subscription_types_keyboard, get_post_options_keyboard, get_yes_no_keyboard
from utils.messages import get_message
from utils.helpers import check_daily_limit, increment_usage
from utils.validators import parse_buttons
from services.subscription_service import check_user_subscription
from services.channel_service import get_user_channels

router = Router()


class PostSchedulerStates(StatesGroup):
    selecting_content_type = State()
    waiting_photo = State()
    waiting_video = State()
    waiting_text = State()
    asking_buttons = State()
    waiting_buttons = State()
    selecting_time = State()


@router.callback_query(F.data == 'post_to_channels')
async def post_to_channels_menu(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    
    async with await get_session() as session:
        query = select(User).where(User.user_id == user_id)
        result = await session.execute(query)
        user = result.scalar_one_or_none()
        
        if not user:
            return
        
        lang = user.language
        
        #check_subscription
        has_subscription = await check_user_subscription(user_id, 'posting') or \
                          await check_user_subscription(user_id, 'premium')
        
        if not has_subscription:
            #check_daily_limit
            can_use = await check_daily_limit(user_id, 'posting', FREE_POSTS_PER_DAY)
            
            if not can_use:
                await callback.message.edit_text(
                    get_message(lang, 'limit_reached'),
                    reply_markup=get_subscription_types_keyboard(lang)
                )
                await callback.answer()
                return
        
        #check_channels
        channels = await get_user_channels(user_id)
        
        if not channels:
            await callback.message.edit_text(
                "У вас нет привязанных каналов. Сначала активируйте подписку на реакции." if lang == 'ru' else "You have no linked channels. First activate reactions subscription.",
                reply_markup=get_back_button(lang)
            )
            await callback.answer()
            return
        
        #select_first_channel_for_now
        await state.update_data(channel_id=channels[0].channel_id)
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📷 Фото" if lang == 'ru' else "📷 Photo", callback_data="post_type_photo")],
            [InlineKeyboardButton(text="🎥 Видео" if lang == 'ru' else "🎥 Video", callback_data="post_type_video")],
            [InlineKeyboardButton(text="📝 Текст" if lang == 'ru' else "📝 Text", callback_data="post_type_text")],
            [InlineKeyboardButton(text="◀️ Назад" if lang == 'ru' else "◀️ Back", callback_data="back_to_menu")]
        ])
        
        await callback.message.edit_text(
            get_message(lang, 'post_content_type'),
            reply_markup=keyboard
        )
        
        await state.set_state(PostSchedulerStates.selecting_content_type)
    
    await callback.answer()


@router.callback_query(F.data == 'post_type_photo', PostSchedulerStates.selecting_content_type)
async def post_type_photo(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    
    await state.update_data(content_type='photo')
    
    async with await get_session() as session:
        query = select(User).where(User.user_id == user_id)
        result = await session.execute(query)
        user = result.scalar_one_or_none()
        
        if user:
            lang = user.language
            
            await callback.message.edit_text(
                get_message(lang, 'send_photo'),
                reply_markup=get_back_button(lang)
            )
            
            await state.set_state(PostSchedulerStates.waiting_photo)
    
    await callback.answer()


@router.message(PostSchedulerStates.waiting_photo, F.photo)
async def process_photo(message: Message, state: FSMContext):
    user_id = message.from_user.id
    
    photo = message.photo[-1]
    caption = message.caption or ''
    
    await state.update_data(
        photo_file_id=photo.file_id,
        caption=caption
    )
    
    async with await get_session() as session:
        query = select(User).where(User.user_id == user_id)
        result = await session.execute(query)
        user = result.scalar_one_or_none()
        
        if user:
            lang = user.language
            
            await message.answer(
                get_message(lang, 'add_buttons'),
                reply_markup=get_yes_no_keyboard('add_buttons_yes', 'add_buttons_no', lang)
            )
            
            await state.set_state(PostSchedulerStates.asking_buttons)


@router.callback_query(F.data == 'add_buttons_yes', PostSchedulerStates.asking_buttons)
async def ask_for_buttons(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    
    async with await get_session() as session:
        query = select(User).where(User.user_id == user_id)
        result = await session.execute(query)
        user = result.scalar_one_or_none()
        
        if user:
            lang = user.language
            
            await callback.message.edit_text(
                get_message(lang, 'send_buttons'),
                reply_markup=get_back_button(lang)
            )
            
            await state.set_state(PostSchedulerStates.waiting_buttons)
    
    await callback.answer()


@router.message(PostSchedulerStates.waiting_buttons)
async def process_buttons(message: Message, state: FSMContext):
    user_id = message.from_user.id
    buttons_text = message.text
    
    buttons = parse_buttons(buttons_text)
    
    await state.update_data(buttons=buttons)
    
    await ask_when_to_post(message, state)


@router.callback_query(F.data == 'add_buttons_no', PostSchedulerStates.asking_buttons)
async def skip_buttons(callback: CallbackQuery, state: FSMContext):
    await state.update_data(buttons=[])
    await ask_when_to_post(callback.message, state)
    await callback.answer()


async def ask_when_to_post(message: Message, state: FSMContext):
    user_id = message.from_user.id if hasattr(message, 'from_user') else message.chat.id
    
    async with await get_session() as session:
        query = select(User).where(User.user_id == user_id)
        result = await session.execute(query)
        user = result.scalar_one_or_none()
        
        if user:
            lang = user.language
            
            await message.answer(
                get_message(lang, 'when_post'),
                reply_markup=get_post_options_keyboard(lang)
            )
            
            await state.set_state(PostSchedulerStates.selecting_time)


@router.callback_query(F.data == 'post_now', PostSchedulerStates.selecting_time)
async def post_now(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    data = await state.get_data()
    
    channel_id = data.get('channel_id')
    photo_file_id = data.get('photo_file_id')
    caption = data.get('caption', '')
    buttons = data.get('buttons', [])
    
    async with await get_session() as session:
        query_user = select(User).where(User.user_id == user_id)
        result_user = await session.execute(query_user)
        user = result_user.scalar_one_or_none()
        
        query_channel = select(Channel).where(Channel.channel_id == channel_id)
        result_channel = await session.execute(query_channel)
        channel = result_channel.scalar_one_or_none()
        
        if user and channel:
            lang = user.language
            
            #build_keyboard
            from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
            keyboard = None
            if buttons:
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text=btn['name'], url=btn['url'])]
                    for btn in buttons
                ])
            
            #send_post
            from bot import bot
            try:
                await bot.send_photo(
                    chat_id=channel.channel_tg_id,
                    photo=photo_file_id,
                    caption=caption,
                    reply_markup=keyboard
                )
                
                await callback.message.edit_text(
                    get_message(lang, 'post_published'),
                    reply_markup=get_back_button(lang)
                )
                
                #increment_usage
                await increment_usage(user_id, 'posting')
                
                await state.clear()
                
            except Exception as e:
                await callback.message.edit_text(
                    f"❌ Ошибка публикации: {str(e)}",
                    reply_markup=get_back_button(lang)
                )
    
    await callback.answer()