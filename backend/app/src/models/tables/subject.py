"""Subject and Tag ORM models."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from models.base import Base
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from models.tables.test_library import TestLibrary
    from models.tables.tutor_relationship import StudentPreferredTag, TutorTag
    from models.tables.user import TutorProfile


class Subject(Base):
    __tablename__ = "subjects"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    tutor_profiles: Mapped[list["TutorProfile"]] = relationship(
        back_populates="subject"
    )
    test_library: Mapped[list["TestLibrary"]] = relationship(back_populates="subject")


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    tutor_tags: Mapped[list["TutorTag"]] = relationship(back_populates="tag")
    student_preferred_tags: Mapped[list["StudentPreferredTag"]] = relationship(
        back_populates="tag"
    )
