"""TutorCertification Pydantic schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


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


class TutorCertificationUpdate(BaseModel):
    title: str | None = Field(None, max_length=255)
    file_url: str | None = Field(None, max_length=500)
    is_verified: bool | None = None
