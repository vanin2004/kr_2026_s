import uuid
from typing import List

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.deps import verify_token
from src.db.session import get_db
from src.models.schemas import RecalculateJobsRequest, SuggestionRequest, TutorResponse
from src.services.jobs import recalculate_ratings
from src.services.suggestions import get_suggestions

router = APIRouter()

class TestTutorCreate(BaseModel):
    full_name: str
    specialization: str
    hourly_rate: int
    experience_years: int

@router.post("/test-data")
async def add_test_data(tutor: TestTutorCreate, db: AsyncSession = Depends(get_db)):
    """Добавить тестового репетитора в БД (для отладки)"""
    new_id = uuid.uuid4()
    
    user_query = """
        INSERT INTO api.users (id, email, password_hash, role)
        VALUES (:id, :email, 'hash', 'tutor')
    """
    await db.execute(text(user_query), {
        "id": new_id,
        "email": f"test_{new_id}@example.com"
    })

    query = """
        INSERT INTO api.tutor_profiles 
        (user_id, full_name, specialization, hourly_rate, experience_years, rating_efficiency, rating_communication, rating_overall)
        VALUES (:id, :name, :spec, :rate, :exp, 4.5, 4.8, 4.6)
    """
    await db.execute(text(query), {
        "id": new_id,
        "name": tutor.full_name,
        "spec": tutor.specialization,
        "rate": tutor.hourly_rate,
        "exp": tutor.experience_years
    })
    await db.commit()
    return {"status": "ok", "user_id": new_id}

@router.post("/suggestions", response_model=List[TutorResponse])
async def compute_suggestions(
    request: SuggestionRequest,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(verify_token)
):
    """
    Алгоритм ранжирования репетиторов (Recommendation Engine).
    Возвращает отсортированный по score список преподавателей.
    """
    return await get_suggestions(db, request)

@router.post("/jobs/recalculate-ratings")
async def trigger_recalculate_ratings(
    request: RecalculateJobsRequest,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(verify_token)
):
    """
    Джоб пересчета рейтингов (Bayesian Ratings).
    Высчитывает метрику эффективности и коммуникативности.
    """
    return await recalculate_ratings(db, request.run_efficiency, request.run_communication)
