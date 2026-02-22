import os
import asyncio
from datetime import time
from zoneinfo import ZoneInfo
from telegram.ext import Application, CommandHandler, ConversationHandler, CallbackQueryHandler, JobQueue

from constants import SETTING_TEST, MAIN_MENU, TRAINING, START_TEST
from handles import (
    start, main_menu, training_menu, start_test_menu, handle_answer, next_question, cancel,
    era_diff_menu, settings_menu, continue_intensive_mode, start_test_with_all_questions,
    back_to_training_from_test, save_and_exit_marathon
)
from database import database
from handles.data_event import start_chronology_mode, check_chronology, handle_chronology
from handles.start_menu import check_subscription_after_start, notify_maintenance, send_daily_streak_reminder

MOSCOW_TZ = ZoneInfo("Europe/Moscow")

BOT_TOKEN = os.getenv('BOT_TOKEN')


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(database.init())

    application = Application.builder().token(BOT_TOKEN).job_queue(JobQueue()).build()

    async def startup_tasks(app):
        await notify_maintenance(app)

        app.job_queue.run_daily(
            send_daily_streak_reminder,
            time=time(hour=12, minute=37, tzinfo=MOSCOW_TZ),
            days=(0,1,2,3,4,5,6),  # каждый день недели
            name="daily_streak",
        )

    application.post_init = startup_tasks

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            MAIN_MENU: [
                CallbackQueryHandler(main_menu, pattern='^(training|intensive|marathon|streak|stats|back_main)$'),
                CallbackQueryHandler(check_subscription_after_start, pattern='^check_sub_after_start$'),
            ],
            TRAINING: [
                CallbackQueryHandler(training_menu,
                                     pattern='^(chronology|date_event|event_date|back_main|back_training|continue_marathon)$')
            ],
            SETTING_TEST: [
                CallbackQueryHandler(era_diff_menu,
                                     pattern='^(difficulty|era|date_event|event_date|back_training|start_test|continue_marathon)$'),
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
                CallbackQueryHandler(handle_chronology, pattern='^chronology_'),
                CallbackQueryHandler(check_chronology, pattern='^check_chronology$'),
                CallbackQueryHandler(start_chronology_mode, pattern='^chronology_retry$'),
                CallbackQueryHandler(save_and_exit_marathon, pattern='^save_and_exit$'),
            ]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    application.add_handler(conv_handler)

    application.run_polling()


if __name__ == '__main__':
    main()