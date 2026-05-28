from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel


class ScheduleSlot(BaseModel):
    day_of_week: int
    start_time: str
    end_time: str

class SuggestionWeights(BaseModel):
    k1_effectiveness: float = 0.30
    k2_communication: float = 0.15
    k3_expertise: float = 0.20
    k4_responsiveness: float = 0.15
    k5_tags: float = 0.20

class SuggestionRequest(BaseModel):
    subject_id: int
    max_price: Optional[int] = None
    min_experience: Optional[int] = 0
    verified_only: Optional[bool] = False
    schedule_slots: Optional[List[ScheduleSlot]] = None
    required_tag_ids: Optional[List[int]] = None
    weights: Optional[SuggestionWeights] = None

class ScoreBreakdown(BaseModel):
    o1: float
    o2: float
    o3: float
    o4: float
    o5: float

class SuggestionResponse(BaseModel):
    tutor_id: UUID
    full_name: Optional[str]
    score: float
    score_breakdown: ScoreBreakdown
    hourly_rate: Optional[int]
    is_new: bool
