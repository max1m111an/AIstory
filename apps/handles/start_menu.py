from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from assets import getMainMenu, getTrainingOptionalMenu, choose_train_menu, main_menu_keybord
from assets.Menu import back_menu_keyboard, subscribe_keyboard
from constants import MAIN_MENU, TRAINING
from handles.db_handles import add_user, get_user_by_telegram_id, get_all_users
from telegram.ext import Application
from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import Forbidden
import asyncio

async def check_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    user_id = update.effective_user.id

    try:
        chat_member = await context.bot.get_chat_member(
            chat_id="-1003732977673",
            user_id=user_id
        )

        subscribed_statuses = ['member', 'administrator', 'creator']

        return chat_member.status in subscribed_statuses

    except Exception as e:
        print(f"Ошибка при проверке подписки: {e}")
        return False



async def notify_maintenance(application):

    users = await get_all_users()

    for user in users:
        try:
            await application.bot.send_message(
                chat_id=user.telegram_id,   # ✅ правильно
                text=(
                    "⚙️ Бот был перезапущен после технического обслуживания.\n\n"
                    "Пожалуйста, нажмите /start чтобы продолжить работу."
                )
            )

            await asyncio.sleep(0.05)  # защита от flood limit

        except Forbidden:
            print(f"Пользователь {user.telegram_id} заблокировал бота")

        except Exception as e:
            print(f"Не удалось отправить {user.telegram_id}: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработчик команды /start с проверкой подписки"""

    is_subscribed = await check_subscription(update, context)

    if not is_subscribed:
        await update.message.reply_text(
            "🚫 Для использования бота необходимо подписаться на наш канал!\n\n"
            "🔔 После подписки нажмите кнопку 'Я подписался'",
            reply_markup=InlineKeyboardMarkup(subscribe_keyboard)
        )
        return MAIN_MENU

    if "user" not in context.user_data:
        user = update.effective_user
        telegram_id = user.id
        db_user = await add_user(telegram_id)
        context.user_data["user"] = db_user

    reply_markup = InlineKeyboardMarkup(main_menu_keybord)
    await update.message.reply_text(getMainMenu(), reply_markup=reply_markup)
    return MAIN_MENU


get_message_train_type = {
    "training": "тренировки 🎯",
    "marathon": "марафона 🏃",
    "intensive": "интенсива ⚡️"
}


async def check_subscription_after_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Проверяет подписку после нажатия кнопки"""
    query = update.callback_query
    await query.answer()


    is_subscribed = await check_subscription(update, context)

    if not is_subscribed:

        reply_markup = InlineKeyboardMarkup(subscribe_keyboard)

        try:
            await query.edit_message_text(
                "❌ Подписка не найдена!\n\n"
                "Пожалуйста, подпишитесь на канал и нажмите кнопку снова.\n"
                "🔄 Попробуйте ещё раз",
                reply_markup=reply_markup
            )
        except Exception as e:
            if "Message is not modified" in str(e):
                await query.message.reply_text(
                    "❌ Подписка всё ещё не найдена!\n\n"
                    "Пожалуйста, подпишитесь на канал и нажмите кнопку снова.",
                    reply_markup=reply_markup
                )
            else:
                raise e

        return MAIN_MENU

    if "user" not in context.user_data:
        user = update.effective_user
        telegram_id = user.id
        db_user = await add_user(telegram_id)
        context.user_data["user"] = db_user

    reply_markup = InlineKeyboardMarkup(main_menu_keybord)

    await query.edit_message_text(
        getMainMenu(),
        reply_markup=reply_markup
    )
    return MAIN_MENU


async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    is_subscribed = await check_subscription(update, context)

    if not is_subscribed:
        await query.message.reply_text(
            "🚫 Для использования бота необходимо подписаться на наш канал!\n\n"
            "🔔 После подписки нажмите кнопку 'Я подписался'",
            reply_markup=InlineKeyboardMarkup(subscribe_keyboard)
        )
        return MAIN_MENU

    if "user" not in context.user_data:
        user = update.effective_user
        telegram_id = user.id
        db_user = await add_user(telegram_id)
        context.user_data["user"] = db_user

    if query.data in ['training', 'marathon', 'intensive']:
        if query.data == 'marathon':
            reply_markup = InlineKeyboardMarkup(choose_train_menu[1:])
        else:
            reply_markup = InlineKeyboardMarkup(choose_train_menu)

        await query.edit_message_text(
            getTrainingOptionalMenu(query.data),
            reply_markup=reply_markup
        )
        context.user_data['train_type'] = query.data
        return TRAINING

    elif query.data == 'back_main':
        reply_markup = InlineKeyboardMarkup(main_menu_keybord)
        await query.edit_message_text(
            getMainMenu(),
            reply_markup=reply_markup
        )
        return MAIN_MENU

    elif query.data == 'stats':
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

        # Формируем сообщение
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