"""User Pydantic schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class UserRead(BaseModel):
    id: UUID
    email: str
    role: str
    created_at: datetime

    model_config = {"from_attributes": True}
