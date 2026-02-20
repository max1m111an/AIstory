from telegram import InlineKeyboardButton

main_menu_keybord = [
        [InlineKeyboardButton("🎯 Тренировка", callback_data='training')],
        [InlineKeyboardButton("⚡ Интенсив", callback_data='intensive')],
        [InlineKeyboardButton("🏃 Марафон", callback_data='marathon')],
        [InlineKeyboardButton("🔥 Держи стрик", callback_data='streak')],
        [InlineKeyboardButton("📊 Моя статистика", callback_data='stats')],
    ]

choose_train_menu = [
        [InlineKeyboardButton("Хронология", callback_data='chronology')],
        [InlineKeyboardButton("Дата - Событие", callback_data='date_event')],
        [InlineKeyboardButton("Событие - Дата", callback_data='event_date')],
        [InlineKeyboardButton("⬅️ Назад", callback_data='back_main')],
]

era_diff_keyboard = [
        [InlineKeyboardButton("🏺 Эпоха", callback_data='era')],
        [InlineKeyboardButton("🎚 Сложность", callback_data='difficulty')],
]

notification_and_back_keyboard = [
        [InlineKeyboardButton("🔕 Уведомления", callback_data='notifications')],
        [InlineKeyboardButton("⬅️ Назад", callback_data='back_training')],
]
back_menu_keyboard = [
        [InlineKeyboardButton("⬅️ Назад", callback_data='back_main')],
]

subscribe_keyboard = [
            [InlineKeyboardButton("📢 Подписаться на канал", url="https://t.me/aisthistory")],
            [InlineKeyboardButton("✅ Я подписался", callback_data="check_sub_after_start")]
        ]