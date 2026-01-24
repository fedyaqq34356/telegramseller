from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy import select
import os

from models.user import User
from config.database import get_session
from config.settings import FREE_CIRCLES_PER_DAY
from utils.keyboards import get_back_button, get_subscription_types_keyboard
from utils.messages import get_message
from utils.helpers import check_daily_limit, increment_usage
from services.subscription_service import check_user_subscription

router = Router()


class VideoCircleStates(StatesGroup):
    waiting_video = State()


@router.callback_query(F.data == 'video_circle')
async def video_circle_menu(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    
    async with await get_session() as session:
        query = select(User).where(User.user_id == user_id)
        result = await session.execute(query)
        user = result.scalar_one_or_none()
        
        if not user:
            return
        
        lang = user.language
        
        #check_subscription
        has_subscription = await check_user_subscription(user_id, 'circles') or \
                          await check_user_subscription(user_id, 'premium')
        
        if not has_subscription:
            #check_daily_limit
            can_use = await check_daily_limit(user_id, 'circles', FREE_CIRCLES_PER_DAY)
            
            if not can_use:
                await callback.message.edit_text(
                    get_message(lang, 'limit_reached'),
                    reply_markup=get_subscription_types_keyboard(lang)
                )
                await callback.answer()
                return
        
        await callback.message.edit_text(
            get_message(lang, 'send_video'),
            reply_markup=get_back_button(lang)
        )
        
        await state.set_state(VideoCircleStates.waiting_video)
    
    await callback.answer()


@router.message(VideoCircleStates.waiting_video, F.video)
async def process_video(message: Message, state: FSMContext):
    user_id = message.from_user.id
    
    async with await get_session() as session:
        query = select(User).where(User.user_id == user_id)
        result = await session.execute(query)
        user = result.scalar_one_or_none()
        
        if not user:
            return
        
        lang = user.language
        
        processing_msg = await message.answer(get_message(lang, 'processing_video'))
        
        try:
            video = message.video
            
            #download_video
            from bot import bot
            file = await bot.get_file(video.file_id)
            file_path = file.file_path
            
            #download_to_temp
            os.makedirs('media/temp', exist_ok=True)
            destination = f'media/temp/{user_id}_{video.file_id}.mp4'
            await bot.download_file(file_path, destination)
            
            #convert_to_video_note_using_ffmpeg
            import subprocess
            output_path = f'media/temp/{user_id}_{video.file_id}_circle.mp4'
            
            cmd = [
                'ffmpeg',
                '-i', destination,
                '-vf', 'crop=min(iw\,ih):min(iw\,ih),scale=640:640',
                '-t', '60',
                '-c:v', 'libx264',
                '-b:v', '1000k',
                output_path
            ]
            
            subprocess.run(cmd, check=True, capture_output=True)
            
            #send_video_note
            with open(output_path, 'rb') as video_file:
                await message.answer_video_note(
                    video_note=video_file
                )
            
            await processing_msg.delete()
            
            await message.answer(
                get_message(lang, 'video_ready'),
                reply_markup=get_back_button(lang)
            )
            
            #increment_usage
            await increment_usage(user_id, 'circles')
            
            #cleanup
            os.remove(destination)
            os.remove(output_path)
            
            await state.clear()
            
        except Exception as e:
            await processing_msg.delete()
            await message.answer(
                f"❌ Ошибка обработки видео: {str(e)}",
                reply_markup=get_back_button(lang)
            )