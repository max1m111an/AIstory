import asyncio

from dotenv import load_dotenv
from database import database
from database.models.user import UserModel

load_dotenv(".env") or load_dotenv("../.env")

async def test_db():
    async with database.session() as session:
        test_user = UserModel(
            username="test_user",
            telegram_id=123456
        )
        session.add(test_user)
        await session.commit()
        await session.refresh()

        print(f"UserModel created: {test_user.username}, ID: {test_user.id}")


if __name__ == "__main__":
    asyncio.run(test_db())