"""TestLibrary and StudentResult ORM models."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from models.base import Base
from models.enums import ResultType
from sqlalchemy import (
    JSON as SA_JSON,
)
from sqlalchemy import (
    DateTime,
    ForeignKey,
    Numeric,
    String,
    func,
)
from sqlalchemy import (
    Enum as SAEnum,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from models.tables.subject import Subject


class TestLibrary(Base):
    __tablename__ = "test_library"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    subject_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("subjects.id"), nullable=False
    )
    topic: Mapped[str] = mapped_column(String(255), nullable=False)
    questions_json: Mapped[dict] = mapped_column(
        SA_JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
    )

    subject: Mapped["Subject"] = relationship("Subject", back_populates="test_library")


class StudentResult(Base):
    __tablename__ = "student_results"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    tutor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    test_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("test_library.id"), nullable=False
    )
    type: Mapped[ResultType] = mapped_column(
        SAEnum(ResultType, name="result_type"), nullable=False
    )
    score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
