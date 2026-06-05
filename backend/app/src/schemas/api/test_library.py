"""TestLibrary Pydantic schemas."""

from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class TestLibraryCreate(BaseModel):
    subject_id: UUID
    topic: str = Field(..., max_length=255)
    questions_json: Any


class TestLibraryRead(BaseModel):
    id: UUID
    subject_id: UUID
    topic: str
    questions_json: Any

    model_config = {"from_attributes": True}


class TestLibraryUpdate(BaseModel):
    topic: str | None = Field(None, max_length=255)
    questions_json: Any | None = None
