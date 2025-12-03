import os
import asyncio

from telegram.ext import Application, CommandHandler, CallbackQueryHandler

from handles import *
from models import TestManager
from database import database


MAIN_MENU, TRAINING, START_TEST = range(3)

BOT_TOKEN = os.getenv('BOT_TOKEN')

test_manager = TestManager()

def main():
    """Основная функция запуска бота"""
    loop = asyncio.get_event_loop()
    loop.run_until_complete(database.init())

    application = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            MAIN_MENU: [
                CallbackQueryHandler(main_menu, pattern='^(training|intensive|marathon|streak|stats|back_main)$')
            ],
            TRAINING: [
                CallbackQueryHandler(training_menu,
                                     pattern='^(chronology|date_event|event_date|back_main|back_training|start_chronology)$')
            ],
            START_TEST: [
                CallbackQueryHandler(start_test_menu, pattern='^(start_test|cancel_test)$'),
                CallbackQueryHandler(handle_answer, pattern='^answer_[1-4]$'),
                CallbackQueryHandler(next_question, pattern='^next_question$'),
                CallbackQueryHandler(main_menu, pattern='^back_main$')
            ]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    application.add_handler(conv_handler)
    application.run_polling()


if __name__ == '__main__':
    main()