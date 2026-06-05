"""Chat Pydantic schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ChatRead(BaseModel):
    id: UUID
    application_id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}
