import os
import asyncio

from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ConversationHandler

from constants import SETTING_TEST, MAIN_MENU, TRAINING, START_TEST
from handles import start, main_menu, training_menu, start_test_menu, handle_answer, next_question, cancel, \
    era_diff_menu, settings_menu, continue_intensive_mode, start_test_with_all_questions, back_to_training_from_test
from database import database


BOT_TOKEN = os.getenv('BOT_TOKEN')


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
                                     pattern='^(chronology|date_event|event_date|back_main|back_training)$')
            ],
            SETTING_TEST: [
                CallbackQueryHandler(era_diff_menu,
                                     pattern='^(difficulty|era|date_event|event_date|back_training|start_test)$'),
                CallbackQueryHandler(settings_menu,
                                     pattern='^(diff_-1|diff_1|diff_2|diff_3|era_-1|era_[0-9]+|event_date|date_event)$')
            ],
            START_TEST: [
                CallbackQueryHandler(start_test_menu, pattern='^cancel_test$'),
                CallbackQueryHandler(handle_answer, pattern='^answer_[1-4]$'),
                CallbackQueryHandler(next_question, pattern='^next_question$'),
                CallbackQueryHandler(main_menu, pattern='^back_main$'),
                CallbackQueryHandler(era_diff_menu, pattern='^(difficulty|era)$'),
                CallbackQueryHandler(start_test_with_all_questions, pattern='^start_test$'),
                CallbackQueryHandler(back_to_training_from_test, pattern='^back_training$'),
                CallbackQueryHandler(continue_intensive_mode, pattern='^continue_intensive$'),
            ]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    application.add_handler(conv_handler)
    application.run_polling()


if __name__ == '__main__':
    main()