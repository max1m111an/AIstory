from io import BytesIO
import pandas as pd
from sqlalchemy import select

from database.models import EraModel
from .db_engine import database
from .models.event import EventModel


async def parse_datafile(file, sheet_name: str) -> pd.DataFrame:
    df = pd.read_excel(file, sheet_name=sheet_name, engine='openpyxl')
    df['Difficulty'] = df['Difficulty'].fillna(0)
    df = df.dropna()
    df['Difficulty'] = df['Difficulty'].astype('int64')
    print(df.info())

    return df


async def load_data_to_db(file_: BytesIO, sheet_='Лист1'):
    result = await parse_datafile(file_, sheet_)
    count: int = 0
    current_eras = {}

    async with database.session() as session:
        temp_db_eras = await session.execute(select(EraModel))
        db_eras = temp_db_eras.all()
        for index, row in result.iterrows():
            try:
                era_name = row['Era']
                if era_name not in db_eras and era_name not in current_eras:
                    new_era = EraModel(
                        name=era_name,
                    )
                    flush_era = await session.merge(new_era)
                    await session.flush()
                    current_eras[era_name] = flush_era.id

                event_to_add = EventModel(
                    name=row['Questions'],
                    date=row['Answer'],
                    difficulty=row['Difficulty'],
                    era_id=flush_era.id,
                )
                session.add(event_to_add)
                await session.commit()
                await session.refresh(event_to_add)
                count += 1

            except Exception as e:
                print(f"load_data_to_db err: {str(e)}")
                await session.rollback()
                continue

    return count
