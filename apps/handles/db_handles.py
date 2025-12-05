from io import BytesIO
from typing import List, Dict

from sqlalchemy import select, and_
from telegram import Update
from telegram.ext import ContextTypes

from database import load_data_to_db, database
from database.models import EventModel, EraModel


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


select_events_stmt = select(EventModel.name, EventModel.date)

async def get_events_name_date() -> List[Dict]:
    """Получает все события из базы данных"""
    async with database.session() as session:
        result = await session.execute(select_events_stmt)
        events = result.all()
        return [{'name': name, 'date': date} for name, date in events]

async def get_eras_name() -> List[Dict]:
    """Получает все эпохи из базы данных"""
    async with database.session() as session:
        result = await session.execute(
            select(EraModel.id, EraModel.name).order_by(EraModel.id)
        )
        eras = result.all()
        return [{'id': id, 'name': name} for id, name in eras]


async def get_events_with_filters(difficulty: int = None, era_id: int = None) -> List[Dict]:
    """Получает ВСЕ события с учетом фильтров сложности и эпохи"""
    async with database.session() as session:
        query = select_events_stmt

        conditions = []
        if difficulty is not None and difficulty != -1:
            conditions.append(EventModel.difficulty == difficulty)
        if era_id is not None and era_id != -1:
            conditions.append(EventModel.era_id == era_id)

        if conditions:
            if len(conditions) > 1:
                query = query.where(and_(*conditions))
            else:
                query = query.where(conditions[0])

        result = await session.execute(query)
        events = result.all()
        return [{'name': name, 'date': date} for name, date in events]
