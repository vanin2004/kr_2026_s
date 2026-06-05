"""Lesson Pydantic schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


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
