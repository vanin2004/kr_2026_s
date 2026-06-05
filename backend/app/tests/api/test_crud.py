"""
CRUD-тесты для базовых сущностей: subjects, tags, users + пагинация/фильтрация.
"""

import uuid

import pytest
from httpx import AsyncClient
from models.tables import Subject, Tag, User

pytestmark = pytest.mark.asyncio


class TestSubjectsCRUD:
    """CRUD для /api/custom/subjects (int PK)."""

    async def test_create_subject(self, client: AsyncClient):
        """POST /api/custom/subjects — создание предмета."""
        response = await client.post("/api/custom/subjects", json={"name": "Chemistry"})
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Chemistry"
        assert "id" in data

    async def test_list_subjects(
        self, client: AsyncClient, seed_subjects: list[Subject]
    ):
        """GET /api/custom/subjects — список предметов."""
        response = await client.get("/api/custom/subjects")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 3
        names = {item["name"] for item in data}
        assert "Mathematics" in names
        assert "Physics" in names

    async def test_get_subject_by_id(
        self, client: AsyncClient, seed_subjects: list[Subject]
    ):
        """GET /api/custom/subjects/{id} — получение предмета по ID."""
        subject_id = seed_subjects[0].id
        response = await client.get(f"/api/custom/subjects/{subject_id}")
        assert response.status_code == 200
        assert response.json()["name"] == "Mathematics"

    async def test_get_subject_not_found(self, client: AsyncClient):
        """GET /api/custom/subjects с несуществующим UUID — 404."""
        response = await client.get(f"/api/custom/subjects/{uuid.uuid4()}")
        assert response.status_code == 404

    async def test_update_subject(
        self, client: AsyncClient, seed_subjects: list[Subject]
    ):
        """PATCH /api/custom/subjects/{id} — обновление предмета."""
        subject_id = seed_subjects[0].id
        response = await client.patch(
            f"/api/custom/subjects/{subject_id}",
            json={"name": "Advanced Mathematics"},
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Advanced Mathematics"

    async def test_delete_subject(
        self, client: AsyncClient, seed_subjects: list[Subject]
    ):
        """DELETE /api/custom/subjects/{id} — удаление предмета."""
        subject_id = seed_subjects[0].id
        response = await client.delete(f"/api/custom/subjects/{subject_id}")
        assert response.status_code == 204

        # Проверяем, что действительно удалён
        get_response = await client.get(f"/api/custom/subjects/{subject_id}")
        assert get_response.status_code == 404


class TestTagsCRUD:
    """CRUD для /api/custom/tags (int PK)."""

    async def test_create_tag(self, client: AsyncClient):
        """POST /api/custom/tags — создание тега."""
        response = await client.post("/api/custom/tags", json={"name": "olympiad"})
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "olympiad"
        assert "id" in data

    async def test_list_tags(self, client: AsyncClient, seed_tags: list[Tag]):
        """GET /api/custom/tags — список тегов."""
        response = await client.get("/api/custom/tags")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 3
        names = {t["name"] for t in data}
        assert "exam-prep" in names
        assert "beginner" in names
        assert "advanced" in names

    async def test_get_tag_by_id(self, client: AsyncClient, seed_tags: list[Tag]):
        """GET /api/custom/tags/{id} — получение тега по ID."""
        tag_id = seed_tags[0].id
        response = await client.get(f"/api/custom/tags/{tag_id}")
        assert response.status_code == 200
        assert response.json()["name"] == "exam-prep"

    async def test_get_tag_not_found(self, client: AsyncClient):
        """GET /api/custom/tags с несуществующим UUID — 404."""
        response = await client.get(f"/api/custom/tags/{uuid.uuid4()}")
        assert response.status_code == 404

    async def test_update_tag(self, client: AsyncClient, seed_tags: list[Tag]):
        """PATCH /api/custom/tags/{id} — обновление тега."""
        tag_id = seed_tags[0].id
        response = await client.patch(
            f"/api/custom/tags/{tag_id}",
            json={"name": "exam-preparation"},
        )
        assert response.status_code == 200
        assert response.json()["name"] == "exam-preparation"

    async def test_delete_tag(self, client: AsyncClient, seed_tags: list[Tag]):
        """DELETE /api/custom/tags/{id} — удаление тега."""
        tag_id = seed_tags[0].id
        response = await client.delete(f"/api/custom/tags/{tag_id}")
        assert response.status_code == 204

        # Проверяем, что удалён
        get_response = await client.get(f"/api/custom/tags/{tag_id}")
        assert get_response.status_code == 404


class TestUsersCRUD:
    """CRUD для /api/custom/users (UUID PK)."""

    async def test_list_users(self, client: AsyncClient, seed_users: dict[str, User]):
        """GET /api/custom/users — список пользователей."""
        response = await client.get("/api/custom/users")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        emails = {u["email"] for u in data}
        assert "tutor@example.com" in emails
        assert "student@example.com" in emails

    async def test_get_user_by_id(
        self, client: AsyncClient, seed_users: dict[str, User]
    ):
        """GET /api/custom/users/{user_id} — получение пользователя."""
        tutor = seed_users["tutor"]
        response = await client.get(f"/api/custom/users/{tutor.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "tutor@example.com"
        assert data["role"] == "tutor"

    async def test_get_user_not_found(self, client: AsyncClient):
        """GET /api/custom/users с несуществующим UUID — 404."""
        fake_id = uuid.uuid4()
        response = await client.get(f"/api/custom/users/{fake_id}")
        assert response.status_code == 404

    async def test_delete_user(self, client: AsyncClient, seed_users: dict[str, User]):
        """DELETE /api/custom/users/{user_id} — удаление пользователя."""
        tutor = seed_users["tutor"]
        response = await client.delete(f"/api/custom/users/{tutor.id}")
        assert response.status_code == 204

        # Проверяем, что удалён
        get_response = await client.get(f"/api/custom/users/{tutor.id}")
        assert get_response.status_code == 404


class TestPaginationAndFiltering:
    """Тесты пагинации и фильтрации."""

    async def test_limit_offset(
        self, client: AsyncClient, seed_subjects: list[Subject]
    ):
        """GET /api/custom/subjects?limit=2&offset=1 — пагинация."""
        response = await client.get("/api/custom/subjects?limit=2&offset=1")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    async def test_limit_max_value(
        self, client: AsyncClient, seed_subjects: list[Subject]
    ):
        """GET /api/custom/subjects?limit=1001 — лимит ограничен 1000."""
        response = await client.get("/api/custom/subjects?limit=1001")
        assert response.status_code == 422

    async def test_negative_offset(self, client: AsyncClient):
        """GET с отрицательным offset — 422."""
        response = await client.get("/api/custom/subjects?offset=-1")
        assert response.status_code == 422

    async def test_postgrest_style_filter(
        self, client: AsyncClient, seed_subjects: list[Subject]
    ):
        """
        GET с PostgREST-стилем фильтрации eq.
        Ручной эндпоинт /subjects не поддерживает _apply_filters,
        поэтому фильтрация по name игнорируется — проверяем, что
        все предметы возвращаются.
        """
        response = await client.get("/api/custom/subjects?name=eq.Mathematics")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
