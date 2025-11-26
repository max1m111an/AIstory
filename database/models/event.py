from sqlalchemy import UniqueConstraint, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class EventModel(Base):
    uid = (
        "name",
        "date",
    )
    __tablename__ = "events"
    __table_args__ = (UniqueConstraint(*uid),)

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    date: Mapped[str] = mapped_column(String(25))
    era_id: Mapped[int | None] = mapped_column(ForeignKey("eras.id"), nullable=True)

    era: Mapped["EraModel | None"] = relationship(
        "EraModel", back_populates="events",
    )


class EraModel(Base):
    uid = (
        "name",
        "period_id",
    )
    __tablename__ = "eras"
    __table_args__ = (UniqueConstraint(*uid),)

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    period_id: Mapped[int | None] = mapped_column(ForeignKey("periods.id"), nullable=True)

    events: Mapped[list[EventModel]] = relationship(
        EventModel, back_populates="era",
    )
    period: Mapped["PeriodModel | None"] = relationship(
        "PeriodModel", back_populates="eras",
    )


class PeriodModel(Base):
    uid = (
        "name",
    )
    __tablename__ = "periods"
    __table_args__ = (UniqueConstraint(*uid),)

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    
    eras: Mapped[list[EraModel]] = relationship(
        EraModel, back_populates="period",
    )
