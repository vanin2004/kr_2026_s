from datetime import time
from uuid import UUID

from pydantic import BaseModel, Field


class ScheduleSlot(BaseModel):
    day_of_week: int = Field(..., ge=1, le=7, description="Day of week (1=Mon, 7=Sun)")
    start_time: time
    end_time: time


class SuggestionWeights(BaseModel):
    k1_effectiveness: float = Field(default=0.30, ge=0.0, le=1.0)
    k2_communication: float = Field(default=0.15, ge=0.0, le=1.0)
    k3_expertise: float = Field(default=0.20, ge=0.0, le=1.0)
    k4_responsiveness: float = Field(default=0.15, ge=0.0, le=1.0)
    k5_tags: float = Field(default=0.20, ge=0.0, le=1.0)

    @property
    def is_normalized(self) -> bool:
        total = (
            self.k1_effectiveness
            + self.k2_communication
            + self.k3_expertise
            + self.k4_responsiveness
            + self.k5_tags
        )
        return abs(total - 1.0) < 0.001


class SuggestionRequest(BaseModel):
    subject_id: UUID
    max_price: int | None = None
    min_experience: int | None = Field(default=0, ge=0)
    verified_only: bool | None = False
    schedule_slots: list[ScheduleSlot] | None = None
    required_tag_ids: list[UUID] | None = None
    weights: SuggestionWeights | None = None


class ScoreBreakdown(BaseModel):
    o1: float
    o2: float
    o3: float
    o4: float
    o5: float


class SuggestionResponse(BaseModel):
    tutor_id: UUID
    full_name: str | None = None
    score: float
    score_breakdown: ScoreBreakdown
    hourly_rate: int | None = None
    is_new: bool
