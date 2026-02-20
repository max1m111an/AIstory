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

        user = await get_user_by_telegram_id(telegram_id)

        if not user:
            await query.edit_message_text(
                "📊 У вас пока нет статистики.\n\nПройдите первый тест!"
            )
            return MAIN_MENU

        training_total = user.training_completed_cards
        training_correct = user.training_true_cards
        training_percent = (training_correct / training_total * 100) if training_total > 0 else 0

        intensive_total = user.intensive_completed_cards
        intensive_correct = user.intensive_true_cards
        intensive_percent = (intensive_correct / intensive_total * 100) if intensive_total > 0 else 0

        marathon_total = user.marathon_completed_cards
        marathon_correct = user.marathon_true_cards
        marathon_percent = (marathon_correct / marathon_total * 100) if marathon_total > 0 else 0

        week_training_total = user.week_training_completed_cards
        week_training_correct = user.week_training_true_cards
        week_training_percent = (week_training_correct / week_training_total * 100) if week_training_total > 0 else 0

        week_intensive_total = user.week_intensive_completed_cards
        week_intensive_correct = user.week_intensive_true_cards
        week_intensive_percent = (
                    week_intensive_correct / week_intensive_total * 100) if week_intensive_total > 0 else 0

        week_marathon_total = user.week_marathon_completed_cards
        week_marathon_correct = user.week_marathon_true_cards
        week_marathon_percent = (week_marathon_correct / week_marathon_total * 100) if week_marathon_total > 0 else 0

        message = (
            f"📊 Ваша статистика\n\n"

            f"📈 Общая статистика:\n"
            f"🎯 Тренировка:\n"
            f"   • Карточки: {training_correct}/{training_total} ({training_percent:.1f}%)\n"
            f"   • Полностью пройдено: {user.training_completed_full}\n"
            f"⚡ Интенсив:\n"
            f"   • Карточки: {intensive_correct}/{intensive_total} ({intensive_percent:.1f}%)\n"
            f"   • Полностью пройдено: {user.intensive_completed_full}\n"
            f"🏃 Марафон:\n"
            f"   • Карточки: {marathon_correct}/{marathon_total} ({marathon_percent:.1f}%)\n"
            f"   • Полностью пройдено: {user.marathon_completed_full}\n\n"

            f"📅 За текущую неделю:\n"
            f"🎯 Тренировка:\n"
            f"   • Карточки: {week_training_correct}/{week_training_total} ({week_training_percent:.1f}%)\n"
            f"   • Полностью пройдено: {user.week_training_completed_full}\n"
            f"⚡ Интенсив:\n"
            f"   • Карточки: {week_intensive_correct}/{week_intensive_total} ({week_intensive_percent:.1f}%)\n"
            f"   • Полностью пройдено: {user.week_intensive_completed_full}\n"
            f"🏃 Марафон:\n"
            f"   • Карточки: {week_marathon_correct}/{week_marathon_total} ({week_marathon_percent:.1f}%)\n"
            f"   • Полностью пройдено: {user.week_marathon_completed_full}\n\n"

            f"🔥 Текущая серия: {user.streak_days} дней"
        )


        reply_markup = InlineKeyboardMarkup(back_menu_keyboard)
        await query.edit_message_text(message, reply_markup=reply_markup)
        return MAIN_MENU

    return MAIN_MENU