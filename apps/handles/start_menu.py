from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from assets import getMainMenu, getTrainingOptionalMenu, choose_train_menu, main_menu_keybord
from constants import MAIN_MENU, TRAINING

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

    if query.data == 'training' or query.data == 'marathon' or query.data == 'intensive':
        reply_markup = InlineKeyboardMarkup(choose_train_menu)
        await query.edit_message_text(getTrainingOptionalMenu(get_message_train_type.get(query.data)), reply_markup=reply_markup)
        context.user_data['train_type'] = query.data
        return TRAINING
    
    elif query.data == 'back_main':
        reply_markup = InlineKeyboardMarkup(main_menu_keybord)
        await query.edit_message_text(getMainMenu(), reply_markup=reply_markup)
        return MAIN_MENU

    return MAIN_MENU