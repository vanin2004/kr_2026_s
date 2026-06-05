"""StudentProfile Pydantic schemas."""

from uuid import UUID

from pydantic import BaseModel


class StudentProfileCreate(BaseModel):
    user_id: UUID
    full_name: str | None = None
    photo_url: str | None = None
    search_weights: dict[str, float] | None = None


class StudentProfileRead(BaseModel):
    user_id: UUID
    full_name: str | None = None
    photo_url: str | None = None
    search_weights: dict[str, float] | None = None

    model_config = {"from_attributes": True}


class StudentProfileUpdate(BaseModel):
    full_name: str | None = None
    photo_url: str | None = None
    search_weights: dict[str, float] | None = None
