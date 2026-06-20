from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config.settings import AVAILABLE_REACTIONS


def get_language_keyboard():
    """Клавиатура выбора языка"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
            InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")
        ]
    ])
    return keyboard


def get_main_menu_keyboard(lang='ru'):
    """Главное меню бота"""
    texts = {
        'ru': {
            'demo': '🎁 Получить демо-доступ (1 день)',
            'buy': '💎 Купить подписку',
            'circle': '🎬 Кружок из видео',
            'post': '📤 Постинг в каналы',
            'settings': '⚙️ Мои настройки',
            'language': '🌐 Сменить язык'
        },
        'en': {
            'demo': '🎁 Get demo access (1 day)',
            'buy': '💎 Buy subscription',
            'circle': '🎬 Video circle',
            'post': '📤 Post to channels',
            'settings': '⚙️ My settings',
            'language': '🌐 Change language'
        }
    }
    
    t = texts.get(lang, texts['ru'])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t['demo'], callback_data="demo_access")],
        [InlineKeyboardButton(text=t['buy'], callback_data="buy_subscription")],
        [InlineKeyboardButton(text=t['circle'], callback_data="video_circle")],
        [InlineKeyboardButton(text=t['post'], callback_data="post_to_channels")],
        [InlineKeyboardButton(text=t['settings'], callback_data="my_settings")],
        [InlineKeyboardButton(text=t['language'], callback_data="change_language")]
    ])
    return keyboard


def get_demo_options_keyboard(lang='ru'):
    """Варианты подключения демо"""
    texts = {
        'ru': {
            'main': '➕ Добавить основного бота в канал',
            'own': '🤖 Создать своего бота',
            'back': '◀️ Назад'
        },
        'en': {
            'main': '➕ Add main bot to channel',
            'own': '🤖 Create your own bot',
            'back': '◀️ Back'
        }
    }
    
    t = texts.get(lang, texts['ru'])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t['main'], callback_data="demo_main_bot")],
        [InlineKeyboardButton(text=t['own'], callback_data="demo_own_bot")],
        [InlineKeyboardButton(text=t['back'], callback_data="back_to_menu")]
    ])
    return keyboard


def get_subscription_types_keyboard(lang='ru'):
    """Типы подписок"""
    texts = {
        'ru': {
            'reactions': '🎯 Просмотры и реакции',
            'circles': '🎬 Кружки из видео (безлимит)',
            'posting': '📤 Постинг в каналы (безлимит)',
            'premium': '👑 Премиум (все функции)',
            'back': '◀️ Назад'
        },
        'en': {
            'reactions': '🎯 Views and reactions',
            'circles': '🎬 Video circles (unlimited)',
            'posting': '📤 Channel posting (unlimited)',
            'premium': '👑 Premium (all features)',
            'back': '◀️ Back'
        }
    }
    
    t = texts.get(lang, texts['ru'])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t['reactions'], callback_data="sub_type_reactions")],
        [InlineKeyboardButton(text=t['circles'], callback_data="sub_type_circles")],
        [InlineKeyboardButton(text=t['posting'], callback_data="sub_type_posting")],
        [InlineKeyboardButton(text=t['premium'], callback_data="sub_type_premium")],
        [InlineKeyboardButton(text=t['back'], callback_data="back_to_menu")]
    ])
    return keyboard


def get_tariffs_keyboard(tariffs, lang='ru'):
    """Клавиатура с тарифами"""
    texts = {
        'ru': {
            'back': '◀️ Назад'
        },
        'en': {
            'back': '◀️ Back'
        }
    }
    
    t = texts.get(lang, texts['ru'])
    
    buttons = []
    for tariff in tariffs:
        text = f"{tariff.views_count} просмотров / {tariff.reactions_count} реакций"
        buttons.append([InlineKeyboardButton(
            text=text,
            callback_data=f"tariff_{tariff.tariff_id}"
        )])
    
    buttons.append([InlineKeyboardButton(text=t['back'], callback_data="back_to_sub_types")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_reactions_keyboard(selected=None, lang='ru'):
    """Клавиатура выбора реакций"""
    if selected is None:
        selected = []
    
    texts = {
        'ru': {
            'done': '✅ Готово',
            'back': '◀️ Назад'
        },
        'en': {
            'done': '✅ Done',
            'back': '◀️ Back'
        }
    }
    
    t = texts.get(lang, texts['ru'])
    
    buttons = []
    row = []
    for i, reaction in enumerate(AVAILABLE_REACTIONS):
        checkmark = "✅ " if reaction in selected else ""
        row.append(InlineKeyboardButton(
            text=f"{checkmark}{reaction}",
            callback_data=f"reaction_{reaction}"
        ))
        if (i + 1) % 4 == 0:
            buttons.append(row)
            row = []
    
    if row:
        buttons.append(row)
    
    buttons.append([InlineKeyboardButton(text=t['done'], callback_data="reactions_done")])
    buttons.append([InlineKeyboardButton(text=t['back'], callback_data="back_to_sub_types")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_period_keyboard(prices, lang='ru'):
    """Выбор периода подписки"""
    texts = {
        'ru': {
            'month': 'месяц',
            'months': 'месяца',
            'months2': 'месяцев',
            'back': '◀️ Назад'
        },
        'en': {
            'month': 'month',
            'months': 'months',
            'months2': 'months',
            'back': '◀️ Back'
        }
    }
    
    t = texts.get(lang, texts['ru'])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"1 {t['month']} - {prices['1m']}₽", callback_data="period_1")],
        [InlineKeyboardButton(text=f"3 {t['months']} - {prices['3m']}₽", callback_data="period_3")],
        [InlineKeyboardButton(text=f"6 {t['months2']} - {prices['6m']}₽", callback_data="period_6")],
        [InlineKeyboardButton(text=f"12 {t['months2']} - {prices['12m']}₽", callback_data="period_12")],
        [InlineKeyboardButton(text=t['back'], callback_data="back_to_sub_types")]
    ])
    return keyboard


def get_payment_methods_keyboard(lang='ru'):
    """Способы оплаты"""
    texts = {
        'ru': {
            'crypto': '💰 Криптовалюта',
            'stars': '⭐ Telegram Stars',
            'back': '◀️ Назад'
        },
        'en': {
            'crypto': '💰 Cryptocurrency',
            'stars': '⭐ Telegram Stars',
            'back': '◀️ Back'
        }
    }
    
    t = texts.get(lang, texts['ru'])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t['crypto'], callback_data="payment_crypto")],
        [InlineKeyboardButton(text=t['stars'], callback_data="payment_stars")],
        [InlineKeyboardButton(text=t['back'], callback_data="back_to_sub_types")]
    ])
    return keyboard


def get_crypto_currencies_keyboard(wallets):
    """Выбор криптовалюты"""
    buttons = []
    for wallet in wallets:
        buttons.append([InlineKeyboardButton(
            text=wallet.currency_name,
            callback_data=f"crypto_{wallet.wallet_id}"
        )])
    
    buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_payment")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_check_payment_keyboard(lang='ru'):
    """Проверить оплату"""
    texts = {
        'ru': {
            'check': '✅ Проверить оплату',
            'cancel': '◀️ Отмена'
        },
        'en': {
            'check': '✅ Check payment',
            'cancel': '◀️ Cancel'
        }
    }
    
    t = texts.get(lang, texts['ru'])
    
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t['check'], callback_data="check_payment")],
        [InlineKeyboardButton(text=t['cancel'], callback_data="back_to_menu")]
    ])


def get_stars_payment_keyboard(stars_amount, lang='ru'):
    """Кнопка оплаты Stars"""
    texts = {
        'ru': {
            'pay': f'Оплатить {stars_amount} ⭐',
            'check': '✅ Проверить оплату',
            'cancel': '◀️ Отмена'
        },
        'en': {
            'pay': f'Pay {stars_amount} ⭐',
            'check': '✅ Check payment',
            'cancel': '◀️ Cancel'
        }
    }
    
    t = texts.get(lang, texts['ru'])
    
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t['pay'], pay=True)],
        [InlineKeyboardButton(text=t['check'], callback_data="check_payment_stars")],
        [InlineKeyboardButton(text=t['cancel'], callback_data="back_to_menu")]
    ])


def get_back_button(lang='ru'):
    """Кнопка назад в главное меню"""
    text = '◀️ В главное меню' if lang == 'ru' else '◀️ Back to menu'
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=text, callback_data="back_to_menu")]
    ])


def get_yes_no_keyboard(yes_callback, no_callback, lang='ru'):
    """Универсальная клавиатура Да/Нет"""
    texts = {
        'ru': {'yes': '✅ Да', 'no': '❌ Нет'},
        'en': {'yes': '✅ Yes', 'no': '❌ No'}
    }
    
    t = texts.get(lang, texts['ru'])
    
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=t['yes'], callback_data=yes_callback),
            InlineKeyboardButton(text=t['no'], callback_data=no_callback)
        ]
    ])


def get_post_options_keyboard(lang='ru'):
    """Опции публикации"""
    texts = {
        'ru': {
            'now': '🚀 Опубликовать сейчас',
            'schedule': '⏰ Отложенная публикация',
            'cancel': '◀️ Отмена'
        },
        'en': {
            'now': '🚀 Publish now',
            'schedule': '⏰ Schedule publication',
            'cancel': '◀️ Cancel'
        }
    }
    
    t = texts.get(lang, texts['ru'])
    
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t['now'], callback_data="post_now")],
        [InlineKeyboardButton(text=t['schedule'], callback_data="post_schedule")],
        [InlineKeyboardButton(text=t['cancel'], callback_data="back_to_menu")]
    ])


# Admin keyboards

def get_admin_menu_keyboard():
    """Главное меню админки"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton(text="📢 Рассылка", callback_data="admin_broadcast")],
        [InlineKeyboardButton(text="📥 Экспорт пользователей", callback_data="admin_export")],
        [InlineKeyboardButton(text="👤 Выдать подписку", callback_data="admin_give_sub")],
        [InlineKeyboardButton(text="⚙️ Настройки бота", callback_data="admin_settings")]
    ])
    return keyboard


def get_broadcast_filters_keyboard():
    """Фильтры для рассылки"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👥 Все пользователи", callback_data="broadcast_all")],
        [InlineKeyboardButton(text="🎯 С фильтрами", callback_data="broadcast_filters")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_menu")]
    ])
    return keyboard


def get_admin_settings_keyboard():
    """Настройки в админке"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Приветственные сообщения", callback_data="admin_set_welcome")],
        [InlineKeyboardButton(text="💰 Управление тарифами", callback_data="admin_set_tariffs")],
        [InlineKeyboardButton(text="🪙 Крипто-кошельки", callback_data="admin_set_wallets")],
        [InlineKeyboardButton(text="⭐ Настройки Stars", callback_data="admin_set_stars")],
        [InlineKeyboardButton(text="💎 Цены на доп. функции", callback_data="admin_set_prices")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_menu")]
    ])
    return keyboard