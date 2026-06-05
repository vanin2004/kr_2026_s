"""StudentPreferredTag Pydantic schemas."""

from uuid import UUID

from pydantic import BaseModel


class StudentPreferredTagCreate(BaseModel):
    student_id: UUID
    tag_id: UUID
    is_required: bool = False


class StudentPreferredTagRead(BaseModel):
    student_id: UUID
    tag_id: UUID
    is_required: bool = False

    model_config = {"from_attributes": True}
