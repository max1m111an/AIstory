import os
import asyncio
from io import BytesIO

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from database import load_data_to_db
from database.db_engine import database
from database.models.user import UserModel


BOT_TOKEN = os.getenv('BOT_TOKEN')


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Привет! ')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Доступные команды:\n/start - начать работу\n/help - помощь')


async def test_db_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда для тестирования БД"""
    try:
        async with database.session() as session:
            existing_user = await session.get(UserModel, 123456)
            if existing_user:
                await update.message.reply_text('✅ Пользователь уже существует в БД!')
                return

            test_user = UserModel(
                username="test_user",
                telegram_id=123456
            )
            session.add(test_user)
            await session.commit()
            await update.message.reply_text('✅ Тест БД выполнен! Пользователь создан.')
    except Exception as e:
        await update.message.reply_text(f'❌ Ошибка БД: {str(e)}')


async def load_datafile_to_db(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    document = update.message.document
    print(document.file_name)
    await update.message.reply_text(f"File: {document.file_name}, Size: {document.file_size}")

    if document.mime_type not in ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                              'application/vnd.ms-excel']:
        await update.message.reply_text(f'Wrong file extension.')

    file = await document.get_file()
    bio = BytesIO()
    await file.download_to_memory(bio)
    try:
        rows_count = await load_data_to_db(bio)
        await update.message.reply_text(f'Loaded {rows_count} rows')
    except Exception as e:
        await update.message.reply_text(f'load_datafile err: {str(e)}')


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(database.init())

    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("testdb", test_db_command))
    application.add_handler(MessageHandler(filters.Document.ALL, load_datafile_to_db))

    application.run_polling()


if __name__ == '__main__':
    main()