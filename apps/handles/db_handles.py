from io import BytesIO
from typing import List, Dict

from sqlalchemy import select
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, ConversationHandler

import database
from database import load_data_to_db
from database.models import EventModel


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


async def get_events_name_date() -> List[Dict]:
    """Получает все события из базы данных"""
    async with database.session() as session:
        result = await session.execute(
            select(EventModel.name, EventModel.date)
        )
        events = result.all()
        return [{'name': name, 'date': date} for name, date in events]

