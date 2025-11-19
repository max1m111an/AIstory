import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv('BOT_TOKEN')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Привет! ')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Доступные команды:\n/start - начать работу\n/help - помощь')

async def handle_hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('И тебе привет!')

def main() -> None:
    if not BOT_TOKEN:
        logging.error("BOT_TOKEN не установлен!")
        return

    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    application.run_polling()

if __name__ == '__main__':
    main()