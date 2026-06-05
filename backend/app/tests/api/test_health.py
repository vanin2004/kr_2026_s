"""
Тесты эндпоинта /health.
"""

import pytest
from httpx import AsyncClient


class TestHealthEndpoint:
    """Тесты эндпоинта /health."""

    @pytest.mark.asyncio
    async def test_health_check_returns_ok(self, client: AsyncClient):
        """GET /health должен возвращать {"status": "ok"} с 200."""
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    @pytest.mark.asyncio
    async def test_health_check_method_not_allowed(self, client: AsyncClient):
        """POST /health должен возвращать 405 Method Not Allowed."""
        response = await client.post("/health")
        assert response.status_code == 405

    @pytest.mark.asyncio
    async def test_health_check_has_no_auth(self, client: AsyncClient):
        """Health check не требует авторизации (должен быть публичным)."""
        response = await client.get("/health")
        assert response.status_code == 200
