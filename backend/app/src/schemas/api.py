"""Pydantic v2 schemas for all CRUD endpoints (replacing PostgREST)."""

from datetime import date, datetime, time
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


# ─── Subjects ───────────────────────────────────────────────────
class SubjectCreate(BaseModel):
    name: str = Field(..., max_length=100)


class SubjectRead(SubjectCreate):
    id: int

    model_config = {"from_attributes": True}


class SubjectUpdate(BaseModel):
    name: str | None = Field(None, max_length=100)


# ─── Tags ───────────────────────────────────────────────────────
class TagCreate(BaseModel):
    name: str = Field(..., max_length=100)


class TagRead(TagCreate):
    id: int

    model_config = {"from_attributes": True}


class TagUpdate(BaseModel):
    name: str | None = Field(None, max_length=100)


# ─── Users ──────────────────────────────────────────────────────
class UserRead(BaseModel):
    id: UUID
    email: str
    role: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Tutor Profiles ─────────────────────────────────────────────
class TutorProfileCreate(BaseModel):
    user_id: UUID
    full_name: str | None = None
    photo_url: str | None = None
    education: str | None = None
    subject_id: int | None = None
    hourly_rate: int | None = None
    experience_years: int = 0
    is_verified: bool = False
    student_count: int = 0


class TutorProfileRead(BaseModel):
    user_id: UUID
    full_name: str | None = None
    photo_url: str | None = None
    education: str | None = None
    subject_id: int | None = None
    hourly_rate: int | None = None
    experience_years: int = 0
    is_verified: bool = False
    student_count: int = 0
    rating_efficiency: Decimal | None = None
    rating_communication: Decimal | None = None
    rating_expertise: Decimal | None = None
    rating_responsiveness: Decimal | None = None
    is_new_boost: bool = True

    model_config = {"from_attributes": True}


class TutorProfileUpdate(BaseModel):
    full_name: str | None = None
    photo_url: str | None = None
    education: str | None = None
    subject_id: int | None = None
    hourly_rate: int | None = None
    experience_years: int | None = None
    is_verified: bool | None = None
    is_new_boost: bool | None = None


# ─── Student Profiles ───────────────────────────────────────────
class StudentProfileCreate(BaseModel):
    user_id: UUID
    full_name: str | None = None
    photo_url: str | None = None
    search_weights: dict[str, float] | None = None


class StudentProfileRead(BaseModel):
    user_id: UUID
    full_name: str | None = None
    photo_url: str | None = None
    search_weights: dict[str, float] | None = None

    model_config = {"from_attributes": True}


class StudentProfileUpdate(BaseModel):
    full_name: str | None = None
    photo_url: str | None = None
    search_weights: dict[str, float] | None = None


# ─── Tutor Tags ─────────────────────────────────────────────────
class TutorTagCreate(BaseModel):
    tutor_id: UUID
    tag_id: int


class TutorTagRead(BaseModel):
    tutor_id: UUID
    tag_id: int

    model_config = {"from_attributes": True}


# ─── Student Preferred Tags ─────────────────────────────────────
class StudentPreferredTagCreate(BaseModel):
    student_id: UUID
    tag_id: int
    is_required: bool = False


class StudentPreferredTagRead(BaseModel):
    student_id: UUID
    tag_id: int
    is_required: bool = False

    model_config = {"from_attributes": True}


# ─── Tutor Certifications ───────────────────────────────────────
class TutorCertificationCreate(BaseModel):
    tutor_id: UUID
    title: str = Field(..., max_length=255)
    file_url: str = Field(..., max_length=500)


class TutorCertificationRead(BaseModel):
    id: int
    tutor_id: UUID
    title: str
    file_url: str
    is_verified: bool = False
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Schedules ──────────────────────────────────────────────────
class ScheduleCreate(BaseModel):
    tutor_id: UUID
    day_of_week: int | None = Field(None, ge=1, le=7)
    specific_date: date | None = None
    start_time: time
    end_time: time


class ScheduleRead(BaseModel):
    id: int
    tutor_id: UUID
    day_of_week: int | None = None
    specific_date: date | None = None
    start_time: time
    end_time: time

    model_config = {"from_attributes": True}


class ScheduleUpdate(BaseModel):
    day_of_week: int | None = Field(None, ge=1, le=7)
    specific_date: date | None = None
    start_time: time | None = None
    end_time: time | None = None


# ─── Lessons ────────────────────────────────────────────────────
class LessonCreate(BaseModel):
    student_id: UUID
    tutor_id: UUID
    start_datetime: datetime
    end_datetime: datetime
    meeting_link: str | None = None


class LessonRead(BaseModel):
    id: UUID
    student_id: UUID
    tutor_id: UUID
    start_datetime: datetime
    end_datetime: datetime
    status: str
    meeting_link: str | None = None

    model_config = {"from_attributes": True}


class LessonUpdate(BaseModel):
    status: str | None = None
    meeting_link: str | None = None


# ─── Applications ───────────────────────────────────────────────
class ApplicationCreate(BaseModel):
    student_id: UUID
    tutor_id: UUID


class ApplicationRead(BaseModel):
    id: UUID
    student_id: UUID
    tutor_id: UUID
    status: str
    created_at: datetime
    responded_at: datetime | None = None

    model_config = {"from_attributes": True}


class ApplicationUpdate(BaseModel):
    status: str | None = None


# ─── Chats ──────────────────────────────────────────────────────
class ChatRead(BaseModel):
    id: UUID
    application_id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Messages ───────────────────────────────────────────────────
class MessageCreate(BaseModel):
    chat_id: UUID
    sender_id: UUID
    text: str


class MessageRead(BaseModel):
    id: UUID
    chat_id: UUID
    sender_id: UUID
    text: str
    created_at: datetime
    is_read: bool = False

    model_config = {"from_attributes": True}


class MessageUpdate(BaseModel):
    is_read: bool | None = None


# ─── Test Library ───────────────────────────────────────────────
class TestLibraryCreate(BaseModel):
    subject_id: int
    topic: str = Field(..., max_length=255)
    questions_json: Any


class TestLibraryRead(BaseModel):
    id: int
    subject_id: int
    topic: str
    questions_json: Any

    model_config = {"from_attributes": True}


# ─── Student Results ────────────────────────────────────────────
class StudentResultCreate(BaseModel):
    student_id: UUID
    tutor_id: UUID
    test_id: int
    type: str


class StudentResultRead(BaseModel):
    id: UUID
    student_id: UUID
    tutor_id: UUID
    test_id: int
    type: str
    score: Decimal | None = None
    assigned_at: datetime
    completed_at: datetime | None = None

    model_config = {"from_attributes": True}


class StudentResultUpdate(BaseModel):
    score: Decimal | None = None
    completed_at: datetime | None = None


# ─── Reviews ────────────────────────────────────────────────────
class ReviewCreate(BaseModel):
    student_id: UUID
    tutor_id: UUID
    lesson_id: UUID | None = None
    communication_score: int = Field(..., ge=1, le=5)
    text: str | None = None


class ReviewRead(BaseModel):
    id: UUID
    student_id: UUID
    tutor_id: UUID
    lesson_id: UUID | None = None
    communication_score: int
    text: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Device Tokens ──────────────────────────────────────────────
class DeviceTokenCreate(BaseModel):
    user_id: UUID
    token: str = Field(..., max_length=500)
    platform: str


class DeviceTokenRead(BaseModel):
    id: int
    user_id: UUID
    token: str
    platform: str
    updated_at: datetime

    model_config = {"from_attributes": True}
