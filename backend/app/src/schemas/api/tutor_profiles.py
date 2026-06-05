"""TutorProfile Pydantic schemas."""

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class TutorProfileCreate(BaseModel):
    user_id: UUID
    full_name: str | None = None
    photo_url: str | None = None
    education: str | None = None
    subject_id: UUID | None = None
    hourly_rate: int | None = None
    experience_years: int = 0
    is_verified: bool = False
    student_count: int = 0


class TutorProfileRead(BaseModel):
    user_id: UUID
    full_name: str | None = None
    photo_url: str | None = None
    education: str | None = None
    subject_id: UUID | None = None
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
    subject_id: UUID | None = None
    hourly_rate: int | None = None
    experience_years: int | None = None
    is_verified: bool | None = None
    is_new_boost: bool | None = None
