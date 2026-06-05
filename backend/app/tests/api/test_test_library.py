"""
CRUD-тесты для test_library и device_tokens.
"""

import uuid

import pytest
from httpx import AsyncClient
from models.tables import DeviceToken, Subject, TestLibrary, User

pytestmark = pytest.mark.asyncio


class TestTestLibraryCRUD:
    """CRUD для /api/custom/test_library."""

    async def test_create_test_library(
        self, client: AsyncClient, seed_subjects: list[Subject]
    ):
        """POST /api/custom/test_library — создание теста в библиотеке."""
        response = await client.post(
            "/api/custom/test_library",
            json={
                "subject_id": str(seed_subjects[0].id),
                "topic": "Algebra Basics",
                "questions_json": {"questions": [{"q": "2+2?", "a": "4"}]},
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["topic"] == "Algebra Basics"
        assert "id" in data

    async def test_list_test_library(
        self, client: AsyncClient, seed_test_library: TestLibrary
    ):
        """GET /api/custom/test_library — список тестов."""
        response = await client.get("/api/custom/test_library")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert data[0]["topic"] == "Algebra Basics"

    async def test_list_test_library_filter_by_subject(
        self,
        client: AsyncClient,
        seed_test_library: TestLibrary,
        seed_subjects: list[Subject],
    ):
        """GET /api/custom/test_library?subject_id=... — фильтрация."""
        subject_id = seed_subjects[0].id
        response = await client.get(f"/api/custom/test_library?subject_id={subject_id}")
        assert response.status_code == 200
        assert len(response.json()) == 1

        # Несуществующий subject_id
        response = await client.get(
            f"/api/custom/test_library?subject_id={uuid.uuid4()}"
        )
        assert len(response.json()) == 0

    async def test_get_test_library(
        self, client: AsyncClient, seed_test_library: TestLibrary
    ):
        """GET /api/custom/test_library/{id} — получение теста по ID."""
        response = await client.get(f"/api/custom/test_library/{seed_test_library.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(seed_test_library.id)
        assert data["topic"] == "Algebra Basics"

    async def test_get_test_library_not_found(self, client: AsyncClient):
        """GET с несуществующим UUID — 404."""
        response = await client.get(f"/api/custom/test_library/{uuid.uuid4()}")
        assert response.status_code == 404

    async def test_update_test_library(
        self, client: AsyncClient, seed_test_library: TestLibrary
    ):
        """PATCH /api/custom/test_library/{id} — обновление теста."""
        response = await client.patch(
            f"/api/custom/test_library/{seed_test_library.id}",
            json={"topic": "Advanced Algebra"},
        )
        assert response.status_code == 200
        assert response.json()["topic"] == "Advanced Algebra"

    async def test_delete_test_library(
        self, client: AsyncClient, seed_test_library: TestLibrary
    ):
        """DELETE /api/custom/test_library/{id} — удаление теста."""
        response = await client.delete(
            f"/api/custom/test_library/{seed_test_library.id}"
        )
        assert response.status_code == 204

        # Проверяем удаление
        get_resp = await client.get(f"/api/custom/test_library/{seed_test_library.id}")
        assert get_resp.status_code == 404


class TestDeviceTokensCRUD:
    """CRUD для /api/custom/device_tokens."""

    async def test_create_device_token(
        self, client: AsyncClient, seed_users: dict[str, User]
    ):
        """POST /api/custom/device_tokens — создание токена."""
        tutor = seed_users["tutor"]
        response = await client.post(
            "/api/custom/device_tokens",
            json={
                "user_id": str(tutor.id),
                "token": "fcm-token-12345",
                "platform": "android",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["token"] == "fcm-token-12345"
        assert data["platform"] == "android"

    async def test_list_device_tokens(
        self, client: AsyncClient, seed_device_token: DeviceToken
    ):
        """GET /api/custom/device_tokens — список токенов."""
        response = await client.get("/api/custom/device_tokens")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    async def test_list_device_tokens_filter(
        self, client: AsyncClient, seed_device_token: DeviceToken
    ):
        """GET /api/custom/device_tokens?user_id=... — фильтрация."""
        user_id = seed_device_token.user_id
        response = await client.get(f"/api/custom/device_tokens?user_id={user_id}")
        assert response.status_code == 200
        assert len(response.json()) == 1

    async def test_delete_device_token(
        self, client: AsyncClient, seed_device_token: DeviceToken
    ):
        """DELETE /api/custom/device_tokens/{id} — удаление."""
        # Находим id токена через list
        list_resp = await client.get(
            f"/api/custom/device_tokens?user_id={seed_device_token.user_id}"
        )
        token_id = list_resp.json()[0]["id"]

        response = await client.delete(f"/api/custom/device_tokens/{token_id}")
        assert response.status_code == 204

        # Проверяем удаление
        list_resp = await client.get(
            f"/api/custom/device_tokens?user_id={seed_device_token.user_id}"
        )
        assert len(list_resp.json()) == 0

    async def test_get_device_token(
        self, client: AsyncClient, seed_device_token: DeviceToken
    ):
        """GET /api/custom/device_tokens/{id} — получение токена по ID."""
        list_resp = await client.get(
            f"/api/custom/device_tokens?user_id={seed_device_token.user_id}"
        )
        token_id = list_resp.json()[0]["id"]

        response = await client.get(f"/api/custom/device_tokens/{token_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == token_id
        assert data["token"] == seed_device_token.token
        assert data["platform"] == "android"

    async def test_get_device_token_not_found(self, client: AsyncClient):
        """GET с несуществующим ID — 404."""
        response = await client.get("/api/custom/device_tokens/999999")
        assert response.status_code == 404
