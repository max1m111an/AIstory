from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from assets import getMainMenu, getTrainingOptionalMenu, choose_train_menu, main_menu_keybord
from assets.Menu import back_menu_keyboard
from constants import MAIN_MENU, TRAINING
from handles.db_handles import add_user, get_user_by_telegram_id


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    reply_markup = InlineKeyboardMarkup(main_menu_keybord)

    await update.message.reply_text(getMainMenu(), reply_markup=reply_markup)
    return MAIN_MENU


get_message_train_type = {
    "training": "тренировки 🎯",
    "marathon": "марафона 🏃",
    "intensive": "интенсива ⚡️"
}


async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    if "user" not in context.user_data:
        user = update.effective_user
        telegram_id = user.id

        db_user = await add_user(telegram_id)

        context.user_data["user"] = db_user

    if query.data == 'training' or query.data == 'marathon' or query.data == 'intensive':
        reply_markup = InlineKeyboardMarkup(choose_train_menu) if query.data != 'marathon' else InlineKeyboardMarkup(choose_train_menu[1:])
        await query.edit_message_text(getTrainingOptionalMenu(query.data), reply_markup=reply_markup)
        context.user_data['train_type'] = query.data
        return TRAINING
    
    elif query.data == 'back_main':
        reply_markup = InlineKeyboardMarkup(main_menu_keybord)
        await query.edit_message_text(getMainMenu(), reply_markup=reply_markup)
        return MAIN_MENU

    elif query.data == 'stats':
        query = update.callback_query
        await query.answer()

        user = update.effective_user
        telegram_id = user.id

        db_user = await get_user_by_telegram_id(telegram_id)

        if not db_user:
            await query.edit_message_text(
                "📊 У вас пока нет статистики.\n\nПройдите первый тест!"
            )
            return MAIN_MENU

        text = (
            f"📊 Ваша статистика\n\n"

            f"📈 Общая статистика:\n"
            f"• Всего ответов: {}\n"
            f"• Правильных: {}\n"
            f"• Неправильных: {}\n"
            f"• Процент: {:.1f}%\n\n"

            f"📅 За текущую неделю:\n"
            f"• Ответов: {}\n"
            f"• Правильных: {}\n"
            f"• Неправильных: {}\n"
            f"• Процент: {:.1f}%\n"
        )


        reply_markup = InlineKeyboardMarkup(back_menu_keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup)
        return MAIN_MENU

    return MAIN_MENU