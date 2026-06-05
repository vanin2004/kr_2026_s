"""Application Pydantic schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


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
