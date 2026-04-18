from sqlalchemy import UniqueConstraint, String
from sqlalchemy.orm import Mapped, mapped_column

from database import Base

class CultureModel(Base):
    uid = (
        "img_name",
        "date",
        "build_name",
        "author",
        "city",
        "king",
        "style",
    )
    __tablename__ = "cultures"
    __table_args__ = (UniqueConstraint(*uid),)

    id: Mapped[int] = mapped_column(primary_key=True)
    img_name: Mapped[str] = mapped_column(String(25))
    build_name: Mapped[str] = mapped_column(String(50))
    author: Mapped[str] = mapped_column(String(25))
    date: Mapped[str] = mapped_column(String(25))
    city: Mapped[str] = mapped_column(String(25))
    king: Mapped[str] = mapped_column(String(25))
    style: Mapped[str] = mapped_column(String(25))
