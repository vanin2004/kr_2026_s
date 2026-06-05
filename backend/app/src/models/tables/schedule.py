"""Schedule ORM model."""

from __future__ import annotations

import uuid
from datetime import date, time
from typing import TYPE_CHECKING

from models.base import Base
from sqlalchemy import CheckConstraint, Date, ForeignKey, Integer, Time
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from models.tables.user import User


class Schedule(Base):
    __tablename__ = "schedules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tutor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    day_of_week: Mapped[int | None] = mapped_column(
        Integer, CheckConstraint("day_of_week BETWEEN 1 AND 7")
    )
    specific_date: Mapped[date | None] = mapped_column(Date)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)

    __table_args__ = (
        CheckConstraint(
            "(day_of_week IS NOT NULL AND specific_date IS NULL) OR "
            "(day_of_week IS NULL AND specific_date IS NOT NULL)",
            name="schedule_type_check",
        ),
    )

    tutor: Mapped["User"] = relationship("User", back_populates="schedules")
