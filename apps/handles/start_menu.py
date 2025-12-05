from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from assets import getMainMenu, getTrainingMenu, choose_train_menu, main_menu_keybord
from constants import MAIN_MENU, TRAINING, START_TEST, SETTING_TEST

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    reply_markup = InlineKeyboardMarkup(main_menu_keybord)

    await update.message.reply_text(getMainMenu(), reply_markup=reply_markup)
    return MAIN_MENU


async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    if query.data == 'training':
        reply_markup = InlineKeyboardMarkup(choose_train_menu)
        await query.edit_message_text(getTrainingMenu(), reply_markup=reply_markup)
        return TRAINING

    elif query.data == 'back_main':
        reply_markup = InlineKeyboardMarkup(main_menu_keybord)
        await query.edit_message_text(getMainMenu(), reply_markup=reply_markup)
        return MAIN_MENU

    return MAIN_MENU