import asyncio

from dotenv import load_dotenv
from sqlalchemy import select
from database import database
from database.models.user import User

load_dotenv(".env") or load_dotenv("../.env")

async def test_db():
    await database.init()

    async with database.session() as session:
        test_user = User(
            username="test_user",
            telegram_id=123456
        )
        session.add(test_user)
        await session.commit()

        stmt = select(User).where(User.username == "test_user")
        result = await session.execute(stmt)
        user = result.scalar()

        print(f"User created: {user.username}, ID: {user.id}")


if __name__ == "__main__":
    asyncio.run(test_db())