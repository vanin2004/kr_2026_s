"""
Интеграционные тесты — алгоритм рекомендаций.

Приложение запущено в Docker. Тесты ходят по HTTP через Nginx.
"""

import httpx

from ..conftest import API_BASE, NGINX_URL


class TestSuggestions:
    """Тесты эндпоинта /suggestions."""

    def test_suggestions_basic(self):
        """Базовый запрос рекомендаций."""
        resp = httpx.post(
            f"{NGINX_URL}{API_BASE}/suggestions",
            json={"subject_id": "10000001-0000-0000-0000-000000000001"},
            timeout=10,
        )
        assert resp.status_code == 200
        suggestions = resp.json()
        assert isinstance(suggestions, list)
        if suggestions:
            s = suggestions[0]
            assert "tutor_id" in s
            assert "score" in s
            assert "score_breakdown" in s
            assert "o1" in s["score_breakdown"]

    def test_suggestions_invalid_subject(self):
        """Несуществующий предмет — пустой результат."""
        resp = httpx.post(
            f"{NGINX_URL}{API_BASE}/suggestions",
            json={"subject_id": "00000000-0000-0000-0000-000000000000"},
            timeout=10,
        )
        assert resp.status_code == 200
        assert resp.json() == []

    def test_suggestions_with_filters(self):
        """Рекомендации с фильтрами."""
        resp = httpx.post(
            f"{NGINX_URL}{API_BASE}/suggestions",
            json={
                "subject_id": "10000001-0000-0000-0000-000000000001",
                "max_price": 50000,
                "min_experience": 0,
                "verified_only": False,
            },
            timeout=10,
        )
        assert resp.status_code == 200

    def test_suggestions_with_weights(self):
        """Кастомные веса."""
        resp = httpx.post(
            f"{NGINX_URL}{API_BASE}/suggestions",
            json={
                "subject_id": "10000001-0000-0000-0000-000000000001",
                "weights": {
                    "k1_effectiveness": 0.50,
                    "k2_communication": 0.20,
                    "k3_expertise": 0.10,
                    "k4_responsiveness": 0.10,
                    "k5_tags": 0.10,
                },
            },
            timeout=10,
        )
        assert resp.status_code == 200
        suggestions = resp.json()
        if suggestions:
            assert "score_breakdown" in suggestions[0]
