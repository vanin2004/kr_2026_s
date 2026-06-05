"""Review Pydantic schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


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


class ReviewUpdate(BaseModel):
    communication_score: int | None = Field(None, ge=1, le=5)
    text: str | None = None
