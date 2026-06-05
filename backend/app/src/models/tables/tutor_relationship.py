"""TutorTag, StudentPreferredTag and TutorCertification ORM models."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from models.base import Base
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from models.tables.subject import Tag
    from models.tables.user import User


class TutorTag(Base):
    __tablename__ = "tutor_tags"

    tutor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    tag_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True
    )

    tutor: Mapped["User"] = relationship(
        "User", back_populates="tutor_tags", foreign_keys=[tutor_id]
    )
    tag: Mapped["Tag"] = relationship("Tag", back_populates="tutor_tags")


class StudentPreferredTag(Base):
    __tablename__ = "student_preferred_tags"

    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    tag_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True
    )
    is_required: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    student: Mapped["User"] = relationship(
        "User", back_populates="student_preferred_tags", foreign_keys=[student_id]
    )
    tag: Mapped["Tag"] = relationship("Tag", back_populates="student_preferred_tags")


class TutorCertification(Base):
    __tablename__ = "tutor_certifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tutor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    file_url: Mapped[str] = mapped_column(String(500), nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    tutor: Mapped["User"] = relationship("User", back_populates="tutor_certifications")
