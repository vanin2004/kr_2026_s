"""Schedule Pydantic schemas."""

from datetime import date, time
from uuid import UUID

from pydantic import BaseModel, Field


class ScheduleCreate(BaseModel):
    tutor_id: UUID
    day_of_week: int | None = Field(None, ge=1, le=7)
    specific_date: date | None = None
    start_time: time
    end_time: time


class ScheduleRead(BaseModel):
    id: int
    tutor_id: UUID
    day_of_week: int | None = None
    specific_date: date | None = None
    start_time: time
    end_time: time

    model_config = {"from_attributes": True}


class ScheduleUpdate(BaseModel):
    day_of_week: int | None = Field(None, ge=1, le=7)
    specific_date: date | None = None
    start_time: time | None = None
    end_time: time | None = None
