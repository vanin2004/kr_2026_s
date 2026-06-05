"""DeviceToken ORM model."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from models.base import Base
from models.enums import DevicePlatform
from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, func
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from models.tables.user import User


class DeviceToken(Base):
    __tablename__ = "device_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    token: Mapped[str] = mapped_column(String(500), unique=True, nullable=False)
    platform: Mapped[DevicePlatform] = mapped_column(
        SAEnum(DevicePlatform, name="device_platform"), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (Index("device_tokens_user_idx", "user_id"),)

    user: Mapped["User"] = relationship("User", back_populates="device_tokens")
