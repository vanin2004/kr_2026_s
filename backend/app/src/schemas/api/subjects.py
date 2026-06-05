"""Subject Pydantic schemas."""

from uuid import UUID

from pydantic import BaseModel, Field


class SubjectCreate(BaseModel):
    name: str = Field(..., max_length=100)


class SubjectRead(SubjectCreate):
    id: UUID

    model_config = {"from_attributes": True}


class SubjectUpdate(BaseModel):
    name: str | None = Field(None, max_length=100)
