import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from src.models.schemas import SuggestionRequest, RecalculateJobsRequest
from src.services.suggestions import get_suggestions
from src.services.jobs import recalculate_ratings

@pytest.mark.asyncio
async def test_get_suggestions_logic():
    # Arrange
    mock_db = AsyncMock()
    mock_result = MagicMock()
    
    # Mocking rows returned by DB (simulating raw SQL fetchall)
    class MockRow:
        def __init__(self, user_id, full_name, specialization, hourly_rate, 
                     experience_years, rating_efficiency, rating_communication, rating_overall, tutor_tags):
            self.user_id = user_id
            self.full_name = full_name
            self.specialization = specialization
            self.hourly_rate = hourly_rate
            self.experience_years = experience_years
            self.rating_efficiency = rating_efficiency
            self.rating_communication = rating_communication
            self.rating_overall = rating_overall
            self.tutor_tags = tutor_tags

    user1 = uuid4()
    user2 = uuid4()
    
    mock_result.fetchall.return_value = [
        MockRow(user1, "Perfect Tutor", "Math", 1000, 5, 5.0, 5.0, 5.0, ["#ege", "#strict"]),
        MockRow(user2, "Average Tutor", "Math", 800, 2, 3.0, 3.0, 3.0, []),
    ]
    mock_db.execute.return_value = mock_result
    
    request = SuggestionRequest(
        subject="Math",
        weight_efficiency=0.5,
        weight_communication=0.5,
        weight_expertise=0.0,
        weight_responsiveness=0.0,
        weight_tags=0.0,
        desired_tags=[]
    )
    
    # Act
    tutors = await get_suggestions(mock_db, request)
    
    # Assert
    assert len(tutors) == 2
    assert tutors[0].user_id == user1
    assert tutors[0].full_name == "Perfect Tutor"
    assert tutors[1].user_id == user2
    assert tutors[0].match_score > tutors[1].match_score

@pytest.mark.asyncio
async def test_recalculate_jobs_logic():
    # Arrange
    mock_db = AsyncMock()
    mock_res = MagicMock()
    mock_res.rowcount = 5
    mock_db.execute.return_value = mock_res
    
    # Act
    result = await recalculate_ratings(mock_db, run_efficiency=True, run_communication=True)
    
    # Assert
    assert result["status"] == "ok"
    assert mock_db.execute.call_count == 2 # one for comm, one for eff
    mock_db.commit.assert_awaited_once()

