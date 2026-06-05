"""
Тесты внутреннего webhook-эндпоинта /api/custom/internal/user-created.
"""

import uuid

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


class _TestInternalWebhook:
    """Тесты внутреннего webhook-эндпоинта /api/custom/internal/user-created."""

    async def test_user_created_tutor(self, client: AsyncClient):
        """POST /api/custom/internal/user-created с ролью tutor."""
        user_id = str(uuid.uuid4())
        response = await client.post(
            "/api/custom/internal/user-created",
            json={
                "userId": user_id,
                "email": "new_tutor@example.com",
                "realmRole": "tutor",
            },
        )
        assert response.status_code == 201
        assert response.json()["status"] == "created"

        # Проверяем, что пользователь создался
        get_resp = await client.get(f"/api/custom/users/{user_id}")
        assert get_resp.status_code == 200
        assert get_resp.json()["role"] == "tutor"

    async def test_user_created_student(self, client: AsyncClient):
        """POST /api/custom/internal/user-created с ролью student."""
        user_id = str(uuid.uuid4())
        response = await client.post(
            "/api/custom/internal/user-created",
            json={
                "userId": user_id,
                "email": "new_student@example.com",
                "realmRole": "student",
            },
        )
        assert response.status_code == 201
        assert response.json()["status"] == "created"

        get_resp = await client.get(f"/api/custom/users/{user_id}")
        assert get_resp.status_code == 200
        assert get_resp.json()["role"] == "student"

    async def test_user_created_duplicate(self, client: AsyncClient):
        """POST — повторный вызов для того же userId должен вернуть already_exists."""
        user_id = str(uuid.uuid4())

        resp1 = await client.post(
            "/api/custom/internal/user-created",
            json={
                "userId": user_id,
                "email": "dup@example.com",
                "realmRole": "tutor",
            },
        )
        assert resp1.status_code == 201

        resp2 = await client.post(
            "/api/custom/internal/user-created",
            json={
                "userId": user_id,
                "email": "dup@example.com",
                "realmRole": "tutor",
            },
        )
        assert resp2.status_code == 201
        assert resp2.json()["status"] == "already_exists"

    async def test_user_created_invalid_role(self, client: AsyncClient):
        """POST с невалидной ролью должен вернуть 400."""
        response = await client.post(
            "/api/custom/internal/user-created",
            json={
                "userId": str(uuid.uuid4()),
                "email": "bad_role@example.com",
                "realmRole": "superadmin",
            },
        )
        assert response.status_code == 400

    async def test_user_created_missing_fields(self, client: AsyncClient):
        """POST без обязательных полей — 422 Validation Error."""
        response = await client.post(
            "/api/custom/internal/user-created",
            json={
                "userId": str(uuid.uuid4()),
            },
        )
        assert response.status_code == 422

    async def test_user_created_invalid_uuid(self, client: AsyncClient):
        """POST с невалидным UUID — 422."""
        response = await client.post(
            "/api/custom/internal/user-created",
            json={
                "userId": "not-a-uuid",
                "email": "test@example.com",
                "realmRole": "student",
            },
        )
        assert response.status_code == 422
