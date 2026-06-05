"""Lesson ORM model."""

from __future__ import annotations

import uuid
from datetime import datetime

from models.base import Base
from models.enums import LessonStatus
from sqlalchemy import DateTime, ForeignKey, Index, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column


class Lesson(Base):
    __tablename__ = "lessons"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    tutor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    start_datetime: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    end_datetime: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    status: Mapped[LessonStatus] = mapped_column(
        SAEnum(LessonStatus, name="lesson_status"),
        default=LessonStatus.planned,
        nullable=False,
    )
    meeting_link: Mapped[str | None] = mapped_column(String(500))

    __table_args__ = (
        Index("lessons_start_idx", "start_datetime"),
        Index("lessons_tutor_idx", "tutor_id"),
        Index("lessons_student_idx", "student_id"),
    )
