from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db
from schemas.suggestions import SuggestionRequest, SuggestionResponse
from services.recommendation import RecommendationService

# from ...core.auth import get_current_user # To be implemented if needed

router = APIRouter()


@router.post("/suggestions", response_model=list[SuggestionResponse])
async def get_suggestions(
    request: SuggestionRequest,
    db: AsyncSession = Depends(get_db),
):
    """Get tutor recommendations based on hard filters and soft scoring."""
    try:
        suggestions = await RecommendationService.get_suggestions(
            request, session=db
        )
        return suggestions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
