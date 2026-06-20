MESSAGES = {
    'ru': {
        'welcome': """👋 Добро пожаловать в бот по накрутке реакций и просмотров!

С помощью этого бота вы сможете:
🎯 Автоматически добавлять реакции на посты в вашем канале
👁 Увеличивать просмотры постов
🎬 Создавать кружки из видео
📤 Планировать публикации в каналы

Выберите действие из меню ниже:""",
        
        'demo_info': """🎁 Демо-доступ на 1 день

Демо-доступ включает:
✅ 5 просмотров на пост
✅ 5 реакций на пост
✅ Автоматическая работа с новыми постами

Для активации демо-доступа выберите один из вариантов:""",
        
        'demo_already_used': "❌ Вы уже использовали демо-доступ",
        
        'demo_main_bot_instruction': """📌 Инструкция по добавлению основного бота:

1. Добавьте бота в ваш ЗАКРЫТЫЙ канал как администратора
2. Выдайте боту следующие права:
   ✅ Публикация сообщений
   ✅ Редактирование сообщений
   ✅ Удаление сообщений
3. После добавления бот автоматически начнет работать

⚠️ Важно: канал должен быть закрытым (приватным)""",
        
        'demo_own_bot_instruction': """🤖 Инструкция по созданию своего бота:

1. Перейдите в @BotFather
2. Отправьте команду /newbot
3. Следуйте инструкциям для создания бота
4. Скопируйте токен бота
5. Отправьте токен мне

После этого:
6. Добавьте ВАШЕГО бота в ваш канал как администратора с теми же правами
7. Я начну управлять вашим ботом для добавления реакций""",
        
        'send_bot_token': "🤖 Отправьте токен вашего бота:",
        
        'invalid_token': "❌ Некорректный токен бота. Попробуйте еще раз.",
        
        'bot_token_saved': "✅ Токен бота сохранен! Теперь добавьте вашего бота в канал как администратора.",
        
        'channel_added': "✅ Канал успешно добавлен!\n\nБот начнет обрабатывать новые посты автоматически.",
        
        'demo_activated': "🎉 Демо-доступ активирован на 1 день!\n\nБот начнет работать с новыми постами.",
        
        'subscription_types': """💎 Выберите тип подписки:

🎯 **Просмотры и реакции**
Автоматическое добавление просмотров и реакций на посты

🎬 **Кружки из видео**
Безлимитное создание кружков из видео

📤 **Постинг в каналы**
Безлимитная публикация и планирование постов

👑 **Премиум**
Все функции бота без ограничений""",
        
        'select_tariff': "📊 Выберите тариф:",
        
        'select_reactions': "😀 Выберите реакции (можно несколько):",
        
        'select_period': "⏰ Выберите период подписки:",
        
        'payment_method': "💳 Выберите способ оплаты:",
        
        'crypto_payment': """💰 Оплата криптовалютой

💵 Сумма: {amount} USDT
📫 Адрес кошелька:

`{address}`

После оплаты отправьте хеш транзакции:""",
        
        'stars_payment': """⭐ Оплата Telegram Stars

💰 Стоимость: {amount} Stars

1. Подпишитесь на канал по ссылке
2. Оплатите подписку Stars
3. Вернитесь сюда и нажмите "Проверить оплату"

{link}""",
        
        'payment_pending': "⏳ Ожидаем оплаты...\n\nПосле оплаты нажмите кнопку проверки.",
        
        'payment_not_found': "❌ Оплата не найдена\n\nПожалуйста, завершите оплату и попробуйте снова.",
        
        'payment_success': "✅ Подписка успешно активирована!\n\n📦 Тип: {type}\n⏰ Период: {period} мес.\n\nСпасибо за покупку!",
        
        'no_subscription': "❌ У вас нет активной подписки\n\nВы можете:\n🎁 Использовать бесплатный лимит (3 в день)\n💎 Купить подписку",
        
        'limit_reached': "⚠️ Дневной лимит исчерпан\n\nВы использовали все бесплатные попытки на сегодня.\nКупите подписку для безлимитного использования!",
        
        'send_video': "🎬 Отправьте видео для создания кружка:",
        
        'processing_video': "⏳ Обрабатываем видео...",
        
        'video_ready': "✅ Кружок готов!",
        
        'post_content_type': "📝 Выберите тип контента:",
        
        'send_photo': "📷 Отправьте фото:",
        
        'send_text': "📝 Отправьте текст поста:",
        
        'add_buttons': "Добавить кнопки со ссылками?",
        
        'send_buttons': "Отправьте кнопки в формате:\nНАЗВАНИЕ КНОПКИ | ССЫЛКА\n\n(можно несколько строк)",
        
        'when_post': "⏰ Когда опубликовать?",
        
        'post_published': "✅ Пост опубликован!",
        
        'post_scheduled': "✅ Пост запланирован на {time}",
        
        'settings_info': """⚙️ Ваши настройки

👤 ID: {user_id}
📅 Регистрация: {date}

💎 Активные подписки:
{subscriptions}

📺 Привязанные каналы:
{channels}""",
        
        'no_channels': "Нет привязанных каналов",
        
        'no_active_subs': "Нет активных подписок",
        
        'back_to_menu': "◀️ В главное меню",
    },
    
    'en': {
        'welcome': """👋 Welcome to the reactions and views bot!

With this bot you can:
🎯 Automatically add reactions to posts in your channel
👁 Increase post views
🎬 Create video circles
📤 Schedule channel posts

Choose an action from the menu below:""",
        
        'demo_info': """🎁 Demo access for 1 day

Demo access includes:
✅ 5 views per post
✅ 5 reactions per post
✅ Automatic work with new posts

To activate demo access, choose one of the options:""",
        
        'demo_already_used': "❌ You have already used demo access",
        
        'demo_main_bot_instruction': """📌 Instructions for adding the main bot:

1. Add the bot to your PRIVATE channel as an administrator
2. Give the bot the following rights:
   ✅ Post messages
   ✅ Edit messages
   ✅ Delete messages
3. After adding, the bot will automatically start working

⚠️ Important: the channel must be private""",
        
        'demo_own_bot_instruction': """🤖 Instructions for creating your own bot:

1. Go to @BotFather
2. Send the /newbot command
3. Follow the instructions to create a bot
4. Copy the bot token
5. Send me the token

After that:
6. Add YOUR bot to your channel as an administrator with the same rights
7. I will start managing your bot to add reactions""",
        
        'send_bot_token': "🤖 Send your bot token:",
        
        'invalid_token': "❌ Invalid bot token. Please try again.",
        
        'bot_token_saved': "✅ Bot token saved! Now add your bot to the channel as an administrator.",
        
        'channel_added': "✅ Channel successfully added!\n\nThe bot will start processing new posts automatically.",
        
        'demo_activated': "🎉 Demo access activated for 1 day!\n\nThe bot will start working with new posts.",
        
        'subscription_types': """💎 Choose subscription type:

🎯 **Views and reactions**
Automatic addition of views and reactions to posts

🎬 **Video circles**
Unlimited video circle creation

📤 **Channel posting**
Unlimited publication and post scheduling

👑 **Premium**
All bot features without limits""",
        
        'select_tariff': "📊 Choose a tariff:",
        
        'select_reactions': "😀 Choose reactions (multiple allowed):",
        
        'select_period': "⏰ Choose subscription period:",
        
        'payment_method': "💳 Choose payment method:",
        
        'crypto_payment': """💰 Cryptocurrency payment

💵 Amount: {amount} USDT
📫 Wallet address:

`{address}`

After payment, send the transaction hash:""",
        
        'stars_payment': """⭐ Telegram Stars payment

💰 Cost: {amount} Stars

1. Subscribe to the channel via the link
2. Pay for the subscription with Stars
3. Come back here and click "Check payment"

{link}""",
        
        'payment_pending': "⏳ Awaiting payment...\n\nAfter payment, click the check button.",
        
        'payment_not_found': "❌ Payment not found\n\nPlease complete the payment and try again.",
        
        'payment_success': "✅ Subscription successfully activated!\n\n📦 Type: {type}\n⏰ Period: {period} months\n\nThank you for your purchase!",
        
        'no_subscription': "❌ You don't have an active subscription\n\nYou can:\n🎁 Use the free limit (3 per day)\n💎 Buy a subscription",
        
        'limit_reached': "⚠️ Daily limit exhausted\n\nYou've used all free attempts for today.\nBuy a subscription for unlimited use!",
        
        'send_video': "🎬 Send a video to create a circle:",
        
        'processing_video': "⏳ Processing video...",
        
        'video_ready': "✅ Circle ready!",
        
        'post_content_type': "📝 Choose content type:",
        
        'send_photo': "📷 Send a photo:",
        
        'send_text': "📝 Send post text:",
        
        'add_buttons': "Add buttons with links?",
        
        'send_buttons': "Send buttons in format:\nBUTTON NAME | LINK\n\n(multiple lines allowed)",
        
        'when_post': "⏰ When to publish?",
        
        'post_published': "✅ Post published!",
        
        'post_scheduled': "✅ Post scheduled for {time}",
        
        'settings_info': """⚙️ Your settings

👤 ID: {user_id}
📅 Registration: {date}

💎 Active subscriptions:
{subscriptions}

📺 Linked channels:
{channels}""",
        
        'no_channels': "No linked channels",
        
        'no_active_subs': "No active subscriptions",
        
        'back_to_menu': "◀️ Back to menu",
    }
}


def get_message(lang: str, key: str, **kwargs) -> str:
    """Получить сообщение на нужном языке с форматированием"""
    message = MESSAGES.get(lang, MESSAGES['ru']).get(key, MESSAGES['ru'][key])
    if kwargs:
        return message.format(**kwargs)
    return message