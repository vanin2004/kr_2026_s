"""
Тесты эндпоинта рекомендаций /api/custom/suggestions.
"""

import uuid

import pytest
from httpx import AsyncClient
from models.tables import Subject, TutorProfile, User

pytestmark = pytest.mark.asyncio


class TestSuggestionsEndpoint:
    """Тесты эндпоинта рекомендаций /api/custom/suggestions."""

    async def test_suggestions_returns_empty_when_no_tutors(
        self, client: AsyncClient, seed_subjects: list[Subject]
    ):
        """POST /api/custom/suggestions — пустой результат если нет репетиторов."""
        response = await client.post(
            "/api/custom/suggestions",
            json={
                "subject_id": str(seed_subjects[0].id),
            },
        )
        assert response.status_code == 200
        assert response.json() == []

    async def test_suggestions_with_valid_tutor_returns_sorted(
        self,
        client: AsyncClient,
        seed_subjects: list[Subject],
        seed_tutor_profile: TutorProfile,
        seed_users: dict[str, User],
    ):
        """POST /api/custom/suggestions — возвращает отсортированные рекомендации."""
        response = await client.post(
            "/api/custom/suggestions",
            json={
                "subject_id": str(seed_subjects[0].id),
            },
        )
        assert response.status_code == 200
        data = response.json()

        if data:
            suggestion = data[0]
            assert "tutor_id" in suggestion
            assert "score" in suggestion
            assert "score_breakdown" in suggestion
            assert "o1" in suggestion["score_breakdown"]
            assert "o2" in suggestion["score_breakdown"]
            assert "o3" in suggestion["score_breakdown"]
            assert "o4" in suggestion["score_breakdown"]
            assert "o5" in suggestion["score_breakdown"]

            scores = [s["score"] for s in data]
            assert scores == sorted(scores, reverse=True)

    async def test_suggestions_with_filters(
        self,
        client: AsyncClient,
        seed_subjects: list[Subject],
        seed_tutor_profile: TutorProfile,
    ):
        """POST /api/custom/suggestions — фильтрация по max_price."""
        response = await client.post(
            "/api/custom/suggestions",
            json={
                "subject_id": str(seed_subjects[0].id),
                "max_price": 30,
            },
        )
        assert response.status_code == 200
        data = response.json()
        # Наш тестовый профиль имеет hourly_rate=50, должен быть отфильтрован
        for tutor in data:
            hr = tutor.get("hourly_rate")
            if hr is not None:
                assert hr <= 30

    async def test_suggestions_with_weights(
        self,
        client: AsyncClient,
        seed_subjects: list[Subject],
        seed_tutor_profile: TutorProfile,
    ):
        """POST /api/custom/suggestions — с кастомными весами."""
        response = await client.post(
            "/api/custom/suggestions",
            json={
                "subject_id": str(seed_subjects[0].id),
                "weights": {
                    "k1_effectiveness": 0.5,
                    "k2_communication": 0.2,
                    "k3_expertise": 0.1,
                    "k4_responsiveness": 0.1,
                    "k5_tags": 0.1,
                },
            },
        )
        assert response.status_code == 200
        data = response.json()
        if data:
            sb = data[0]["score_breakdown"]
            assert "o1" in sb
            assert "o2" in sb

    async def test_suggestions_invalid_subject(self, client: AsyncClient):
        """POST /api/custom/suggestions — несуществующий subject_id."""
        response = await client.post(
            "/api/custom/suggestions",
            json={
                "subject_id": str(uuid.uuid4()),
            },
        )
        assert response.status_code == 200
        assert response.json() == []
