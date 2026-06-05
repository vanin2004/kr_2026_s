"""TutorTag Pydantic schemas."""

from uuid import UUID

from pydantic import BaseModel


class TutorTagCreate(BaseModel):
    tutor_id: UUID
    tag_id: UUID


class TutorTagRead(BaseModel):
    tutor_id: UUID
    tag_id: UUID

    model_config = {"from_attributes": True}
