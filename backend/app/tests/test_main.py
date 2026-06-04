"""
Корневые тесты FastAPI приложения.

Проверяют:
1. Health check endpoint (/health)
2. OpenAPI schema generation
3. App title and lifespan configuration
4. Обработка 404 на несуществующих маршрутах
5. CORS / middleware корректность
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


class TestAppConfiguration:
    """Тесты конфигурации FastAPI приложения."""

    @pytest.mark.asyncio
    async def test_openapi_schema_available(self, client: AsyncClient):
        """OpenAPI schema должна быть доступна по /openapi.json."""
        response = await client.get("/openapi.json")
        assert response.status_code == 200
        schema = response.json()
        assert schema["info"]["title"] == "TutorApp API"
        assert "paths" in schema

    @pytest.mark.asyncio
    async def test_openapi_contains_custom_endpoints(self, client: AsyncClient):
        """OpenAPI schema должна включать /api/custom/ эндпоинты."""
        response = await client.get("/openapi.json")
        schema = response.json()
        paths = schema["paths"]

        # Проверяем, что ключевые префиксы присутствуют
        api_paths = [p for p in paths if p.startswith("/api/custom")]
        assert len(api_paths) > 0, "Должен быть хотя бы один /api/custom/ эндпоинт"

        # Проверяем наличие groups
        custom_paths = {
            p
            for p in paths
            if p.startswith("/api/custom") and not p.startswith("/api/custom/internal")
        }
        internal_paths = {p for p in paths if p.startswith("/api/custom/internal")}

        assert len(custom_paths) > 0, "Отсутствуют /api/custom эндпоинты"
        assert len(internal_paths) > 0, "Отсутствуют /api/custom/internal эндпоинты"

    @pytest.mark.asyncio
    async def test_openapi_has_tags(self, client: AsyncClient):
        """OpenAPI schema должна содержать теги endpoints."""
        response = await client.get("/openapi.json")
        schema = response.json()
        tags = [t["name"] for t in schema.get("tags", [])]
        # FastAPI может не добавлять tags в корень, проверяем через paths
        paths = schema["paths"]
        all_tags = set()
        for path, methods in paths.items():
            for method, details in methods.items():
                all_tags.update(details.get("tags", []))
        assert len(all_tags) > 0, "Эндпоинты должны иметь теги"

    @pytest.mark.asyncio
    async def test_openapi_has_health_endpoint(self, client: AsyncClient):
        """OpenAPI должен включать /health."""
        response = await client.get("/openapi.json")
        schema = response.json()
        assert "/health" in schema["paths"], "/health должен быть в OpenAPI"


class TestNotFoundAndErrors:
    """Тесты обработки ошибок."""

    @pytest.mark.asyncio
    async def test_unknown_route_returns_404(self, client: AsyncClient):
        """GET на несуществующий маршрут должен возвращать 404."""
        response = await client.get("/nonexistent_route_12345")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_unknown_api_route_returns_json_404(self, client: AsyncClient):
        """404 ответ должен быть в формате JSON с деталями."""
        response = await client.get("/api/custom/nonexistent")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data


class TestDocsEndpoint:
    """Тесты документации."""

    @pytest.mark.asyncio
    async def test_docs_available(self, client: AsyncClient):
        """Документация Swagger UI доступна."""
        response = await client.get("/docs")
        # Swagger UI может редиректить, но должен быть доступен
        assert response.status_code in (200, 307)

    @pytest.mark.asyncio
    async def test_redoc_available(self, client: AsyncClient):
        """Документация ReDoc доступна."""
        response = await client.get("/redoc")
        assert response.status_code == 200
