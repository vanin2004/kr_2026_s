"""StudentResult Pydantic schemas."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class StudentResultCreate(BaseModel):
    student_id: UUID
    tutor_id: UUID
    test_id: UUID
    type: str


class StudentResultRead(BaseModel):
    id: UUID
    student_id: UUID
    tutor_id: UUID
    test_id: UUID
    type: str
    score: Decimal | None = None
    assigned_at: datetime
    completed_at: datetime | None = None

    model_config = {"from_attributes": True}


class StudentResultUpdate(BaseModel):
    score: Decimal | None = None
    completed_at: datetime | None = None
