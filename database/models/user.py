import datetime

from sqlalchemy import String, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped
from sqlalchemy.sql import func
from sqlalchemy.orm import mapped_column

from database import Base


class UserModel(Base):
    uid = (
        "username",
        "telegram_id",
    )
    __tablename__ = "users"
    __table_args__ = (UniqueConstraint(*uid),)

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(100))
    telegram_id: Mapped[int] = mapped_column()
    created_at: Mapped[datetime.date] = mapped_column(DateTime(timezone=True), server_default=func.now())