"""Tag Pydantic schemas."""

from uuid import UUID

from pydantic import BaseModel, Field


class TagCreate(BaseModel):
    name: str = Field(..., max_length=100)


class TagRead(TagCreate):
    id: UUID

    model_config = {"from_attributes": True}


class TagUpdate(BaseModel):
    name: str | None = Field(None, max_length=100)
