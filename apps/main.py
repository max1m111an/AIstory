import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from database.database import database
from database.models.user import User


BOT_TOKEN = os.getenv('BOT_TOKEN')


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Привет! ')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Доступные команды:\n/start - начать работу\n/help - помощь')


async def test_db_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда для тестирования БД"""
    try:
        async with database.session() as session:
            existing_user = await session.get(User, 123456)
            if existing_user:
                await update.message.reply_text('✅ Пользователь уже существует в БД!')
                return

            test_user = User(
                username="test_user",
                telegram_id=123456
            )
            session.add(test_user)
            await session.commit()
            await update.message.reply_text('✅ Тест БД выполнен! Пользователь создан.')
    except Exception as e:
        await update.message.reply_text(f'❌ Ошибка БД: {str(e)}')


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(database.init())

    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("testdb", test_db_command))

    application.run_polling()


if __name__ == '__main__':
    main()