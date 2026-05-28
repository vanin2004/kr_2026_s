from unittest.mock import AsyncMock, patch

import pytest
from schemas.suggestions import SuggestionRequest, SuggestionWeights
from services.recommendation import RecommendationService


@pytest.mark.asyncio
async def test_recommendation_logic():
    # Mock database response
    mock_db_rows = [
        {
            'user_id': '00000000-0000-0000-0000-000000000001',
            'full_name': 'Tutor 1',
            'hourly_rate': 1000,
            'experience_years': 5,
            'is_verified': True,
            'is_new_boost': False,
            'rating_efficiency': 0.8,
            'rating_communication': 0.9,
            'rating_expertise': 0.7,
            'rating_responsiveness': 0.6,
            'tutor_tags': [1, 2]
        },
        {
            'user_id': '00000000-0000-0000-0000-000000000002',
            'full_name': 'Tutor 2 (High Score)',
            'hourly_rate': 1200,
            'experience_years': 3,
            'is_verified': True,
            'is_new_boost': False,
            'rating_efficiency': 0.95,
            'rating_communication': 0.95,
            'rating_expertise': 0.95,
            'rating_responsiveness': 0.95,
            'tutor_tags': [1, 3]
        }
    ]

    request = SuggestionRequest(
        subject_id=1,
        required_tag_ids=[1, 3],
        weights=SuggestionWeights(
            k1_effectiveness=0.2,
            k2_communication=0.2,
            k3_expertise=0.2,
            k4_responsiveness=0.2,
            k5_tags=0.2
        )
    )

    with patch('db.session.db_pool.fetch', new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = mock_db_rows
        
        results = await RecommendationService.get_suggestions(request)
        
        assert len(results) == 2
        # Tutor 2 should be first because of higher ratings and perfect tag match
        assert results[0].full_name == 'Tutor 2 (High Score)'
        assert results[0].score > results[1].score
        assert results[0].score_breakdown.o5 == 1.0 # Both tags [1, 3] match
        assert results[1].score_breakdown.o5 == 0.5 # Only tag [1] match from [1, 3]
