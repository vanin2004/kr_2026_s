"""DeviceToken Pydantic schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class DeviceTokenCreate(BaseModel):
    user_id: UUID
    token: str = Field(..., max_length=500)
    platform: str


class DeviceTokenRead(BaseModel):
    id: int
    user_id: UUID
    token: str
    platform: str
    updated_at: datetime

    model_config = {"from_attributes": True}
