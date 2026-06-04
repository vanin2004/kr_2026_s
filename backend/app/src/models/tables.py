"""SQLAlchemy ORM models for all database tables.

Reflects the schema defined in backend/db/init.sql.
Uses SQLAlchemy 2.0 async style.
"""

import uuid
from datetime import date, datetime, time
from decimal import Decimal

from models.base import Base
from models.enums import (
    ApplicationStatus,
    DevicePlatform,
    LessonStatus,
    ResultType,
    UserRole,
)
from sqlalchemy import (
    JSON as SA_JSON,
)
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    PrimaryKeyConstraint,
    String,
    Text,
    Time,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Subject(Base):
    __tablename__ = "subjects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    tutor_profiles: Mapped[list["TutorProfile"]] = relationship(
        back_populates="subject"
    )
    test_library: Mapped[list["TestLibrary"]] = relationship(back_populates="subject")


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    tutor_tags: Mapped[list["TutorTag"]] = relationship(back_populates="tag")
    student_preferred_tags: Mapped[list["StudentPreferredTag"]] = relationship(
        back_populates="tag"
    )


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role"), nullable=False
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
    subject_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("subjects.id"))
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


class TutorTag(Base):
    __tablename__ = "tutor_tags"

    tutor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    tag_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True
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
    tag_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True
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
        Enum(LessonStatus, name="lesson_status"),
        default=LessonStatus.planned,
        nullable=False,
    )
    meeting_link: Mapped[str | None] = mapped_column(String(500))

    __table_args__ = (
        Index("lessons_start_idx", "start_datetime"),
        Index("lessons_tutor_idx", "tutor_id"),
        Index("lessons_student_idx", "student_id"),
    )


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    tutor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    status: Mapped[ApplicationStatus] = mapped_column(
        Enum(ApplicationStatus, name="application_status"),
        default=ApplicationStatus.pending,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    responded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    __table_args__ = (UniqueConstraint("student_id", "tutor_id"),)


class Chat(Base):
    __tablename__ = "chats"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    application_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("applications.id"), unique=True, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    messages: Mapped[list["Message"]] = relationship(
        "Message", back_populates="chat", cascade="all, delete-orphan"
    )


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    chat_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("chats.id", ondelete="CASCADE"), nullable=False
    )
    sender_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    __table_args__ = (Index("messages_chat_idx", "chat_id", "created_at"),)

    chat: Mapped["Chat"] = relationship("Chat", back_populates="messages")


class TestLibrary(Base):
    __tablename__ = "test_library"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    subject_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("subjects.id"), nullable=False
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
    test_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("test_library.id"), nullable=False
    )
    type: Mapped[ResultType] = mapped_column(
        Enum(ResultType, name="result_type"), nullable=False
    )
    score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


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


class DeviceToken(Base):
    __tablename__ = "device_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    token: Mapped[str] = mapped_column(String(500), unique=True, nullable=False)
    platform: Mapped[DevicePlatform] = mapped_column(
        Enum(DevicePlatform, name="device_platform"), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (Index("device_tokens_user_idx", "user_id"),)

    user: Mapped["User"] = relationship("User", back_populates="device_tokens")
