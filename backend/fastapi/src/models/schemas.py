from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID

class SuggestionRequest(BaseModel):
    # Hard filters
    subject: Optional[str] = None
    max_rate: Optional[int] = None
    min_experience: Optional[int] = None
    
    # Soft scoring weights (must sum to 1.0 ideally, but we will normalize)
    weight_efficiency: float = 0.30
    weight_communication: float = 0.15
    weight_expertise: float = 0.20
    weight_responsiveness: float = 0.15
    weight_tags: float = 0.20
    
    # Student desired tags
    desired_tags: List[str] = []

class TutorResponse(BaseModel):
    user_id: UUID
    full_name: str
    specialization: Optional[str]
    hourly_rate: Optional[int]
    experience_years: Optional[int]
    match_score: float

class RecalculateJobsRequest(BaseModel):
    run_efficiency: bool = True
    run_communication: bool = True
