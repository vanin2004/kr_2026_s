from typing import List

from fastapi import APIRouter, HTTPException
from schemas.suggestions import SuggestionRequest, SuggestionResponse
from services.recommendation import RecommendationService

# from ...core.auth import get_current_user # To be implemented if needed

router = APIRouter()

@router.post("/suggestions", response_model=List[SuggestionResponse])
async def get_suggestions(request: SuggestionRequest):
    try:
        suggestions = await RecommendationService.get_suggestions(request)
        return suggestions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
