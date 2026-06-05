"""Review ORM model."""

from __future__ import annotations

import uuid
from datetime import datetime

from models.base import Base
from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    tutor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    lesson_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("lessons.id")
    )
    communication_score: Mapped[int] = mapped_column(
        Integer,
        CheckConstraint("communication_score BETWEEN 1 AND 5"),
        nullable=False,
    )
    text: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (UniqueConstraint("student_id", "lesson_id"),)
