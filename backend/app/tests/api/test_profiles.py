"""
CRUD-тесты для профилей: tutor_profiles, student_profiles, tutor_certifications,
tutor_tags, student_preferred_tags.
"""

import uuid

import pytest
from httpx import AsyncClient
from models.tables import (
    StudentPreferredTag,
    Subject,
    Tag,
    TutorCertification,
    TutorProfile,
    User,
)

pytestmark = pytest.mark.asyncio


class TestTutorProfilesCRUD:
    """CRUD для /api/custom/tutor_profiles (UUID PK)."""

    async def test_list_tutor_profiles(
        self, client: AsyncClient, seed_tutor_profile: TutorProfile
    ):
        """GET /api/custom/tutor_profiles — список профилей."""
        response = await client.get("/api/custom/tutor_profiles")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        names = {p["full_name"] for p in data}
        assert "John Doe" in names

    async def test_create_tutor_profile(
        self,
        client: AsyncClient,
        seed_users: dict[str, User],
        seed_subjects: list[Subject],
    ):
        """POST /api/custom/tutor_profiles — создание профиля."""
        tutor = seed_users["tutor"]
        # Сначала удаляем профиль, созданный фикстурой seed_tutor_profile
        # (но фикстура не вызвана, так что проблем нет)
        response = await client.post(
            "/api/custom/tutor_profiles",
            json={
                "user_id": str(tutor.id),
                "full_name": "Jane Smith",
                "subject_id": str(seed_subjects[0].id),
                "hourly_rate": 60,
                "experience_years": 8,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["full_name"] == "Jane Smith"
        assert data["hourly_rate"] == 60

    async def test_get_tutor_profile(
        self, client: AsyncClient, seed_tutor_profile: TutorProfile
    ):
        """GET /api/custom/tutor_profiles/{user_id} — получение профиля."""
        response = await client.get(
            f"/api/custom/tutor_profiles/{seed_tutor_profile.user_id}"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == "John Doe"
        assert data["hourly_rate"] == 50

    async def test_get_tutor_profile_not_found(self, client: AsyncClient):
        """GET с несуществующим user_id — 404."""
        fake_id = uuid.uuid4()
        response = await client.get(f"/api/custom/tutor_profiles/{fake_id}")
        assert response.status_code == 404

    async def test_update_tutor_profile(
        self, client: AsyncClient, seed_tutor_profile: TutorProfile
    ):
        """PATCH /api/custom/tutor_profiles/{user_id} — обновление."""
        response = await client.patch(
            f"/api/custom/tutor_profiles/{seed_tutor_profile.user_id}",
            json={"hourly_rate": 75, "full_name": "John Updated"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["hourly_rate"] == 75
        assert data["full_name"] == "John Updated"

    async def test_delete_tutor_profile(
        self, client: AsyncClient, seed_tutor_profile: TutorProfile
    ):
        """DELETE /api/custom/tutor_profiles/{user_id} — удаление."""
        response = await client.delete(
            f"/api/custom/tutor_profiles/{seed_tutor_profile.user_id}"
        )
        assert response.status_code == 204

        # Проверяем удаление
        get_response = await client.get(
            f"/api/custom/tutor_profiles/{seed_tutor_profile.user_id}"
        )
        assert get_response.status_code == 404


class TestStudentProfilesCRUD:
    """CRUD для /api/custom/student_profiles (UUID PK)."""

    async def test_get_student_profile_not_found(self, client: AsyncClient):
        """GET /api/custom/student_profiles/{id} — 404 для несуществующего."""
        fake_id = uuid.uuid4()
        response = await client.get(f"/api/custom/student_profiles/{fake_id}")
        assert response.status_code == 404

    async def test_create_student_profile(
        self, client: AsyncClient, seed_users: dict[str, User]
    ):
        """POST /api/custom/student_profiles — создание профиля студента."""
        student = seed_users["student"]
        response = await client.post(
            "/api/custom/student_profiles",
            json={
                "user_id": str(student.id),
                "full_name": "Alice Wonderland",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["full_name"] == "Alice Wonderland"
        assert data["user_id"] == str(student.id)

    async def test_get_student_profile(
        self, client: AsyncClient, seed_users: dict[str, User]
    ):
        """GET /api/custom/student_profiles/{id} — получение профиля студента."""
        student = seed_users["student"]
        # Сначала создаём профиль
        await client.post(
            "/api/custom/student_profiles",
            json={
                "user_id": str(student.id),
                "full_name": "Alice Wonderland",
            },
        )

        # Затем получаем
        response = await client.get(f"/api/custom/student_profiles/{student.id}")
        assert response.status_code == 200
        assert response.json()["full_name"] == "Alice Wonderland"

    async def test_list_student_profiles(
        self, client: AsyncClient, seed_users: dict[str, User]
    ):
        """GET /api/custom/student_profiles — список профилей учеников."""
        student = seed_users["student"]
        await client.post(
            "/api/custom/student_profiles",
            json={"user_id": str(student.id), "full_name": "Alice"},
        )
        response = await client.get("/api/custom/student_profiles")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert any(p["full_name"] == "Alice" for p in data)

    async def test_delete_student_profile(
        self, client: AsyncClient, seed_users: dict[str, User]
    ):
        """DELETE /api/custom/student_profiles/{id} — удаление профиля."""
        student = seed_users["student"]
        await client.post(
            "/api/custom/student_profiles",
            json={"user_id": str(student.id), "full_name": "ToDelete"},
        )

        response = await client.delete(f"/api/custom/student_profiles/{student.id}")
        assert response.status_code == 204

        # Проверяем удаление
        get_resp = await client.get(f"/api/custom/student_profiles/{student.id}")
        assert get_resp.status_code == 404

    async def test_update_student_profile(
        self, client: AsyncClient, seed_users: dict[str, User]
    ):
        """PATCH /api/custom/student_profiles/{id} — обновление профиля."""
        student = seed_users["student"]
        # Создаём
        await client.post(
            "/api/custom/student_profiles",
            json={
                "user_id": str(student.id),
                "full_name": "Alice",
            },
        )

        # Обновляем
        response = await client.patch(
            f"/api/custom/student_profiles/{student.id}",
            json={"full_name": "Alice Updated"},
        )
        assert response.status_code == 200
        assert response.json()["full_name"] == "Alice Updated"

    async def test_create_student_profile_with_weights(
        self, client: AsyncClient, seed_users: dict[str, User]
    ):
        """POST с кастомными search_weights."""
        student = seed_users["student"]
        response = await client.post(
            "/api/custom/student_profiles",
            json={
                "user_id": str(student.id),
                "full_name": "Bob",
                "search_weights": {
                    "k1_effectiveness": 0.4,
                    "k2_communication": 0.3,
                    "k3_expertise": 0.1,
                    "k4_responsiveness": 0.1,
                    "k5_tags": 0.1,
                },
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["search_weights"]["k1_effectiveness"] == 0.4


class TestTutorCertificationsCRUD:
    """CRUD для /api/custom/tutor_certifications."""

    async def test_create_tutor_certification(
        self, client: AsyncClient, seed_users: dict[str, User]
    ):
        """POST /api/custom/tutor_certifications — создание сертификата."""
        tutor = seed_users["tutor"]
        response = await client.post(
            "/api/custom/tutor_certifications",
            json={
                "tutor_id": str(tutor.id),
                "title": "Advanced Math Certificate",
                "file_url": "http://example.com/cert.pdf",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Advanced Math Certificate"
        assert not data["is_verified"]
        assert "id" in data

    async def test_list_tutor_certifications(
        self, client: AsyncClient, seed_tutor_certification: TutorCertification
    ):
        """GET /api/custom/tutor_certifications — список сертификатов."""
        response = await client.get("/api/custom/tutor_certifications")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert data[0]["title"] == "Teaching Certificate"

    async def test_list_tutor_certifications_by_tutor(
        self,
        client: AsyncClient,
        seed_tutor_certification: TutorCertification,
        seed_users: dict[str, User],
    ):
        """GET с фильтром tutor_id."""
        tutor = seed_users["tutor"]
        response = await client.get(
            f"/api/custom/tutor_certifications?tutor_id={tutor.id}"
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

        # Другой (несуществующий) tutor_id
        response = await client.get(
            f"/api/custom/tutor_certifications?tutor_id={uuid.uuid4()}"
        )
        assert response.status_code == 200
        assert len(response.json()) == 0

    async def test_get_tutor_certification(
        self,
        client: AsyncClient,
        seed_tutor_certification: TutorCertification,
    ):
        """GET /api/custom/tutor_certifications/{id} — получение сертификата."""
        cert_id = seed_tutor_certification.id
        response = await client.get(f"/api/custom/tutor_certifications/{cert_id}")
        assert response.status_code == 200
        assert response.json()["title"] == "Teaching Certificate"
        assert response.json()["id"] == cert_id

    async def test_get_tutor_certification_not_found(self, client: AsyncClient):
        """GET с несуществующим ID — 404."""
        response = await client.get("/api/custom/tutor_certifications/999999")
        assert response.status_code == 404

    async def test_update_tutor_certification(
        self,
        client: AsyncClient,
        seed_tutor_certification: TutorCertification,
    ):
        """PATCH /api/custom/tutor_certifications/{id} — обновление (подтверждение)."""
        cert_id = seed_tutor_certification.id
        response = await client.patch(
            f"/api/custom/tutor_certifications/{cert_id}",
            json={"is_verified": True},
        )
        assert response.status_code == 200
        assert response.json()["is_verified"] is True

        # Обновление заголовка
        response = await client.patch(
            f"/api/custom/tutor_certifications/{cert_id}",
            json={"title": "Updated Certificate"},
        )
        assert response.status_code == 200
        assert response.json()["title"] == "Updated Certificate"

    async def test_delete_tutor_certification(
        self,
        client: AsyncClient,
        seed_tutor_certification: TutorCertification,
    ):
        """DELETE /api/custom/tutor_certifications/{id} — удаление."""
        cert_id = seed_tutor_certification.id
        response = await client.delete(f"/api/custom/tutor_certifications/{cert_id}")
        assert response.status_code == 204

        # Проверяем удаление
        get_resp = await client.get(f"/api/custom/tutor_certifications/{cert_id}")
        assert get_resp.status_code == 404


class TestTutorTagsCompositePK:
    """Тесты для /api/custom/tutor_tags (составной PK)."""

    async def test_create_tutor_tag(
        self, client: AsyncClient, seed_users: dict[str, User], seed_tags: list[Tag]
    ):
        """POST /api/custom/tutor_tags — создание связи."""
        tutor = seed_users["tutor"]
        tag = seed_tags[0]

        response = await client.post(
            "/api/custom/tutor_tags",
            json={
                "tutor_id": str(tutor.id),
                "tag_id": str(tag.id),
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["tutor_id"] == str(tutor.id)
        assert data["tag_id"] == str(tag.id)

    async def test_list_tutor_tags(
        self, client: AsyncClient, seed_users: dict[str, User], seed_tags: list[Tag]
    ):
        """GET /api/custom/tutor_tags — список связей."""
        tutor = seed_users["tutor"]
        for tag in seed_tags[:2]:
            await client.post(
                "/api/custom/tutor_tags",
                json={
                    "tutor_id": str(tutor.id),
                    "tag_id": str(tag.id),
                },
            )

        response = await client.get("/api/custom/tutor_tags")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    async def test_list_tutor_tags_filter_by_tutor(
        self, client: AsyncClient, seed_users: dict[str, User], seed_tags: list[Tag]
    ):
        """GET /api/custom/tutor_tags?tutor_id=... — фильтрация."""
        tutor = seed_users["tutor"]
        await client.post(
            "/api/custom/tutor_tags",
            json={
                "tutor_id": str(tutor.id),
                "tag_id": str(seed_tags[0].id),
            },
        )

        response = await client.get(f"/api/custom/tutor_tags?tutor_id={tutor.id}")
        assert response.status_code == 200
        assert len(response.json()) == 1

    async def test_delete_tutor_tag(
        self, client: AsyncClient, seed_users: dict[str, User], seed_tags: list[Tag]
    ):
        """DELETE /api/custom/tutor_tags — удаление связи."""
        tutor = seed_users["tutor"]
        tag = seed_tags[0]

        # Create
        await client.post(
            "/api/custom/tutor_tags",
            json={
                "tutor_id": str(tutor.id),
                "tag_id": str(tag.id),
            },
        )

        # Delete
        delete_resp = await client.delete(
            "/api/custom/tutor_tags",
            params={"tutor_id": str(tutor.id), "tag_id": str(tag.id)},
        )
        assert delete_resp.status_code == 204

        # Проверяем что удалено
        list_resp = await client.get("/api/custom/tutor_tags")
        assert len(list_resp.json()) == 0


class TestStudentPreferredTagsCRUD:
    """CRUD для /api/custom/student_preferred_tags (составной PK)."""

    async def test_create_student_preferred_tag(
        self, client: AsyncClient, seed_users: dict[str, User], seed_tags: list[Tag]
    ):
        """POST /api/custom/student_preferred_tags — создание."""
        student = seed_users["student"]
        tag = seed_tags[0]
        response = await client.post(
            "/api/custom/student_preferred_tags",
            json={
                "student_id": str(student.id),
                "tag_id": str(tag.id),
                "is_required": True,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["student_id"] == str(student.id)
        assert data["tag_id"] == str(tag.id)
        assert data["is_required"] is True

    async def test_list_student_preferred_tags(
        self, client: AsyncClient, seed_student_preferred_tag: StudentPreferredTag
    ):
        """GET /api/custom/student_preferred_tags — список."""
        response = await client.get("/api/custom/student_preferred_tags")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    async def test_list_student_preferred_tags_filter(
        self, client: AsyncClient, seed_users: dict[str, User], seed_tags: list[Tag]
    ):
        """GET с фильтром student_id."""
        student = seed_users["student"]
        # Create
        await client.post(
            "/api/custom/student_preferred_tags",
            json={
                "student_id": str(student.id),
                "tag_id": str(seed_tags[0].id),
            },
        )

        response = await client.get(
            f"/api/custom/student_preferred_tags?student_id={student.id}"
        )
        assert response.status_code == 200
        assert len(response.json()) == 1

    async def test_delete_student_preferred_tag(
        self, client: AsyncClient, seed_users: dict[str, User], seed_tags: list[Tag]
    ):
        """DELETE /api/custom/student_preferred_tags — удаление."""
        student = seed_users["student"]
        tag = seed_tags[0]

        await client.post(
            "/api/custom/student_preferred_tags",
            json={
                "student_id": str(student.id),
                "tag_id": str(tag.id),
            },
        )

        delete_resp = await client.delete(
            "/api/custom/student_preferred_tags",
            params={"student_id": str(student.id), "tag_id": str(tag.id)},
        )
        assert delete_resp.status_code == 204

        list_resp = await client.get("/api/custom/student_preferred_tags")
        assert len(list_resp.json()) == 0
