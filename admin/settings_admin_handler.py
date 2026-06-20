from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy import select

from models.subscription import Tariff
from models.settings import CryptoWallet
from config.database import get_session
from utils.decorators import admin_only
from utils.keyboards import get_admin_settings_keyboard
from utils.helpers import get_admin_setting, set_admin_setting

router = Router()


class AdminSettingsStates(StatesGroup):
    waiting_welcome_ru = State()
    waiting_welcome_en = State()
    waiting_circles_price = State()
    waiting_posting_price = State()
    waiting_premium_price = State()
    adding_wallet_currency = State()
    adding_wallet_address = State()
    adding_tariff_name = State()
    adding_tariff_views = State()
    adding_tariff_reactions = State()
    adding_tariff_prices = State()


@router.callback_query(F.data == 'admin_settings')
@admin_only
async def admin_settings_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "⚙️ Настройки бота",
        reply_markup=get_admin_settings_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == 'admin_set_welcome')
@admin_only
async def set_welcome_messages(callback: CallbackQuery, state: FSMContext):
    current_ru = await get_admin_setting('welcome_message_ru', 'Не установлено')
    current_en = await get_admin_setting('welcome_message_en', 'Not set')
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="set_welcome_ru")],
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="set_welcome_en")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_settings")]
    ])
    
    await callback.message.edit_text(
        f"📝 Приветственные сообщения\n\n🇷🇺 Русский:\n{current_ru[:100]}...\n\n🇬🇧 English:\n{current_en[:100]}...\n\nВыберите язык для редактирования:",
        reply_markup=keyboard
    )
    await callback.answer()


@router.callback_query(F.data == 'set_welcome_ru')
@admin_only
async def set_welcome_ru(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("📝 Отправьте новое приветственное сообщение на русском:")
    await state.set_state(AdminSettingsStates.waiting_welcome_ru)
    await callback.answer()


@router.message(AdminSettingsStates.waiting_welcome_ru)
@admin_only
async def process_welcome_ru(message: Message, state: FSMContext):
    await set_admin_setting('welcome_message_ru', message.text)
    await message.answer("✅ Приветственное сообщение (RU) обновлено!")
    await state.clear()


@router.callback_query(F.data == 'set_welcome_en')
@admin_only
async def set_welcome_en(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("📝 Send new welcome message in English:")
    await state.set_state(AdminSettingsStates.waiting_welcome_en)
    await callback.answer()


@router.message(AdminSettingsStates.waiting_welcome_en)
@admin_only
async def process_welcome_en(message: Message, state: FSMContext):
    await set_admin_setting('welcome_message_en', message.text)
    await message.answer("✅ Welcome message (EN) updated!")
    await state.clear()


@router.callback_query(F.data == 'admin_set_prices')
@admin_only
async def set_prices_menu(callback: CallbackQuery):
    circles_price = await get_admin_setting('circles_price', '500')
    posting_price = await get_admin_setting('posting_price', '700')
    premium_price = await get_admin_setting('premium_price', '1500')
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"🎬 Кружки: {circles_price}₽", callback_data="set_price_circles")],
        [InlineKeyboardButton(text=f"📤 Постинг: {posting_price}₽", callback_data="set_price_posting")],
        [InlineKeyboardButton(text=f"👑 Премиум: {premium_price}₽", callback_data="set_price_premium")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_settings")]
    ])
    
    await callback.message.edit_text(
        "💎 Цены на дополнительные функции\n\n(цена за 1 месяц)",
        reply_markup=keyboard
    )
    await callback.answer()


@router.callback_query(F.data == 'set_price_circles')
@admin_only
async def set_circles_price(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("💰 Введите новую цену для кружков (за 1 месяц):")
    await state.set_state(AdminSettingsStates.waiting_circles_price)
    await callback.answer()


@router.message(AdminSettingsStates.waiting_circles_price)
@admin_only
async def process_circles_price(message: Message, state: FSMContext):
    try:
        price = float(message.text.strip())
        await set_admin_setting('circles_price', str(price))
        await message.answer(f"✅ Цена на кружки обновлена: {price}₽")
        await state.clear()
    except ValueError:
        await message.answer("❌ Введите корректную цену")


@router.callback_query(F.data == 'admin_set_wallets')
@admin_only
async def manage_wallets(callback: CallbackQuery):
    async with await get_session() as session:
        query = select(CryptoWallet).where(CryptoWallet.is_active == True)
        result = await session.execute(query)
        wallets = result.scalars().all()
        
        text = "🪙 Крипто-кошельки\n\n"
        for wallet in wallets:
            text += f"• {wallet.currency_name}: {wallet.wallet_address[:20]}...\n"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="➕ Добавить кошелек", callback_data="add_wallet")],
            [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_settings")]
        ])
        
        await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data == 'add_wallet')
@admin_only
async def add_wallet(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("💱 Введите название криптовалюты (например, USDT, BTC, ETH):")
    await state.set_state(AdminSettingsStates.adding_wallet_currency)
    await callback.answer()


@router.message(AdminSettingsStates.adding_wallet_currency)
@admin_only
async def process_wallet_currency(message: Message, state: FSMContext):
    currency = message.text.strip().upper()
    await state.update_data(currency=currency)
    await message.answer(f"📫 Теперь отправьте адрес кошелька для {currency}:")
    await state.set_state(AdminSettingsStates.adding_wallet_address)


@router.message(AdminSettingsStates.adding_wallet_address)
@admin_only
async def process_wallet_address(message: Message, state: FSMContext):
    address = message.text.strip()
    data = await state.get_data()
    currency = data.get('currency')
    
    async with await get_session() as session:
        wallet = CryptoWallet(
            currency_name=currency,
            wallet_address=address,
            is_active=True
        )
        session.add(wallet)
        await session.commit()
    
    await message.answer(f"✅ Кошелек добавлен!\n\n{currency}: {address}")
    await state.clear()


@router.callback_query(F.data == 'admin_set_tariffs')
@admin_only
async def manage_tariffs(callback: CallbackQuery):
    async with await get_session() as session:
        query = select(Tariff)
        result = await session.execute(query)
        tariffs = result.scalars().all()
        
        text = "💰 Тарифы\n\n"
        for tariff in tariffs:
            text += f"• {tariff.name}: {tariff.views_count}/{tariff.reactions_count}\n"
            text += f"  Цены: {tariff.price_1m}₽/1м, {tariff.price_3m}₽/3м\n\n"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="➕ Добавить тариф", callback_data="add_tariff")],
            [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_settings")]
        ])
        
        await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data == 'add_tariff')
@admin_only
async def add_tariff(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("📝 Введите название тарифа (например, 5/5, 10/10):")
    await state.set_state(AdminSettingsStates.adding_tariff_name)
    await callback.answer()


@router.message(AdminSettingsStates.adding_tariff_name)
@admin_only
async def process_tariff_name(message: Message, state: FSMContext):
    name = message.text.strip()
    await state.update_data(tariff_name=name)
    await message.answer("👁 Введите количество просмотров:")
    await state.set_state(AdminSettingsStates.adding_tariff_views)


@router.message(AdminSettingsStates.adding_tariff_views)
@admin_only
async def process_tariff_views(message: Message, state: FSMContext):
    try:
        views = int(message.text.strip())
        await state.update_data(views=views)
        await message.answer("😀 Введите количество реакций:")
        await state.set_state(AdminSettingsStates.adding_tariff_reactions)
    except ValueError:
        await message.answer("❌ Введите число")


@router.message(AdminSettingsStates.adding_tariff_reactions)
@admin_only
async def process_tariff_reactions(message: Message, state: FSMContext):
    try:
        reactions = int(message.text.strip())
        await state.update_data(reactions=reactions)
        await message.answer("💰 Введите цены через пробел (1м 3м 6м 12м):\nНапример: 500 1400 2500 4500")
        await state.set_state(AdminSettingsStates.adding_tariff_prices)
    except ValueError:
        await message.answer("❌ Введите число")


@router.message(AdminSettingsStates.adding_tariff_prices)
@admin_only
async def process_tariff_prices(message: Message, state: FSMContext):
    try:
        prices = [float(p) for p in message.text.strip().split()]
        
        if len(prices) != 4:
            await message.answer("❌ Введите 4 цены через пробел")
            return
        
        data = await state.get_data()
        
        async with await get_session() as session:
            tariff = Tariff(
                name=data['tariff_name'],
                views_count=data['views'],
                reactions_count=data['reactions'],
                price_1m=prices[0],
                price_3m=prices[1],
                price_6m=prices[2],
                price_12m=prices[3]
            )
            session.add(tariff)
            await session.commit()
        
        await message.answer(
            f"✅ Тариф добавлен!\n\n{data['tariff_name']}\n{data['views']}/{data['reactions']}\nЦены: {prices}"
        )
        await state.clear()
        
    except ValueError:
        await message.answer("❌ Введите корректные цены")