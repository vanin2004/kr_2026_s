"""User, TutorProfile and StudentProfile ORM models."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from models.base import Base
from models.enums import UserRole
from models.tables.device import DeviceToken
from models.tables.schedule import Schedule
from models.tables.subject import Subject
from models.tables.tutor_relationship import (
    StudentPreferredTag,
    TutorCertification,
    TutorTag,
)
from sqlalchemy import (
    JSON as SA_JSON,
)
from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy import (
    Enum as SAEnum,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    role: Mapped[UserRole] = mapped_column(
        SAEnum(UserRole, name="user_role"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    tutor_profile: Mapped["TutorProfile | None"] = relationship(
        "TutorProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    student_profile: Mapped["StudentProfile | None"] = relationship(
        "StudentProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    tutor_tags: Mapped[list["TutorTag"]] = relationship(
        "TutorTag",
        back_populates="tutor",
        cascade="all, delete-orphan",
        foreign_keys="TutorTag.tutor_id",
    )
    student_preferred_tags: Mapped[list["StudentPreferredTag"]] = relationship(
        "StudentPreferredTag",
        back_populates="student",
        cascade="all, delete-orphan",
        foreign_keys="StudentPreferredTag.student_id",
    )
    tutor_certifications: Mapped[list["TutorCertification"]] = relationship(
        "TutorCertification", back_populates="tutor", cascade="all, delete-orphan"
    )
    schedules: Mapped[list["Schedule"]] = relationship(
        "Schedule", back_populates="tutor", cascade="all, delete-orphan"
    )
    device_tokens: Mapped[list["DeviceToken"]] = relationship(
        "DeviceToken", back_populates="user", cascade="all, delete-orphan"
    )


class TutorProfile(Base):
    __tablename__ = "tutor_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    full_name: Mapped[str | None] = mapped_column(String(255))
    photo_url: Mapped[str | None] = mapped_column(String(500))
    education: Mapped[str | None] = mapped_column(Text)
    subject_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("subjects.id")
    )
    hourly_rate: Mapped[int | None] = mapped_column(Integer)
    experience_years: Mapped[int] = mapped_column(Integer, default=0)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    student_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    rating_efficiency: Mapped[Decimal | None] = mapped_column(Numeric(4, 3))
    rating_communication: Mapped[Decimal | None] = mapped_column(Numeric(4, 3))
    rating_expertise: Mapped[Decimal | None] = mapped_column(Numeric(4, 3))
    rating_responsiveness: Mapped[Decimal | None] = mapped_column(Numeric(4, 3))
    is_new_boost: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="tutor_profile")
    subject: Mapped["Subject | None"] = relationship(
        "Subject", back_populates="tutor_profiles"
    )


class StudentProfile(Base):
    __tablename__ = "student_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    full_name: Mapped[str | None] = mapped_column(String(255))
    photo_url: Mapped[str | None] = mapped_column(String(500))
    search_weights: Mapped[dict] = mapped_column(
        SA_JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
        default={
            "k1_effectiveness": 0.30,
            "k2_communication": 0.15,
            "k3_expertise": 0.20,
            "k4_responsiveness": 0.15,
            "k5_tags": 0.20,
        },
    )

    user: Mapped["User"] = relationship("User", back_populates="student_profile")
