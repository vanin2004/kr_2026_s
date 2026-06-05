"""Message Pydantic schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class MessageCreate(BaseModel):
    chat_id: UUID
    sender_id: UUID
    text: str


class MessageRead(BaseModel):
    id: UUID
    chat_id: UUID
    sender_id: UUID
    text: str
    created_at: datetime
    is_read: bool = False

    model_config = {"from_attributes": True}


class MessageUpdate(BaseModel):
    is_read: bool | None = None
