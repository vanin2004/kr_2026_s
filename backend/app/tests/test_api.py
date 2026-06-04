"""
Тесты API эндпоинтов FastAPI.

Покрывают все CRUD-эндпоинты, бизнес-логику (suggestions, webhook),
пагинацию и валидацию. Используют in-memory SQLite через conftest.py фикстуры,
не требуют внешней БД или Keycloak.
"""

import uuid
from datetime import datetime, timezone

import pytest
from httpx import AsyncClient
from models.tables import (
    Application,
    Chat,
    DeviceToken,
    Lesson,
    Message,
    Review,
    Schedule,
    StudentPreferredTag,
    StudentProfile,
    StudentResult,
    Subject,
    Tag,
    TestLibrary,
    TutorCertification,
    TutorProfile,
    User,
)

# =========================================================================
# ЧАСТЬ 1. CRUD-тесты
# =========================================================================


class TestSubjectsCRUD:
    """CRUD для /api/custom/subjects (int PK)."""

    @pytest.mark.asyncio
    async def test_create_subject(self, client: AsyncClient):
        """POST /api/custom/subjects — создание предмета."""
        response = await client.post("/api/custom/subjects", json={"name": "Chemistry"})
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Chemistry"
        assert "id" in data

    @pytest.mark.asyncio
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

    @pytest.mark.asyncio
    async def test_get_subject_by_id(
        self, client: AsyncClient, seed_subjects: list[Subject]
    ):
        """GET /api/custom/subjects/{id} — получение предмета по ID."""
        subject_id = seed_subjects[0].id
        response = await client.get(f"/api/custom/subjects/{subject_id}")
        assert response.status_code == 200
        assert response.json()["name"] == "Mathematics"

    @pytest.mark.asyncio
    async def test_get_subject_not_found(self, client: AsyncClient):
        """GET /api/custom/subjects/99999 — 404 для несуществующего ID."""
        response = await client.get("/api/custom/subjects/99999")
        assert response.status_code == 404

    @pytest.mark.asyncio
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

    @pytest.mark.asyncio
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

    @pytest.mark.asyncio
    async def test_create_tag(self, client: AsyncClient):
        """POST /api/custom/tags — создание тега."""
        response = await client.post("/api/custom/tags", json={"name": "olympiad"})
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "olympiad"
        assert "id" in data

    @pytest.mark.asyncio
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

    @pytest.mark.asyncio
    async def test_get_tag_by_id(self, client: AsyncClient, seed_tags: list[Tag]):
        """GET /api/custom/tags/{id} — получение тега по ID."""
        tag_id = seed_tags[0].id
        response = await client.get(f"/api/custom/tags/{tag_id}")
        assert response.status_code == 200
        assert response.json()["name"] == "exam-prep"

    @pytest.mark.asyncio
    async def test_get_tag_not_found(self, client: AsyncClient):
        """GET /api/custom/tags/99999 — 404."""
        response = await client.get("/api/custom/tags/99999")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_tag(self, client: AsyncClient, seed_tags: list[Tag]):
        """PATCH /api/custom/tags/{id} — обновление тега."""
        tag_id = seed_tags[0].id
        response = await client.patch(
            f"/api/custom/tags/{tag_id}",
            json={"name": "exam-preparation"},
        )
        assert response.status_code == 200
        assert response.json()["name"] == "exam-preparation"

    @pytest.mark.asyncio
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

    @pytest.mark.asyncio
    async def test_list_users(self, client: AsyncClient, seed_users: dict[str, User]):
        """GET /api/custom/users — список пользователей."""
        response = await client.get("/api/custom/users")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        emails = {u["email"] for u in data}
        assert "tutor@example.com" in emails
        assert "student@example.com" in emails

    @pytest.mark.asyncio
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

    @pytest.mark.asyncio
    async def test_get_user_not_found(self, client: AsyncClient):
        """GET /api/custom/users с несуществующим UUID — 404."""
        fake_id = uuid.uuid4()
        response = await client.get(f"/api/custom/users/{fake_id}")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_user(self, client: AsyncClient, seed_users: dict[str, User]):
        """DELETE /api/custom/users/{user_id} — удаление пользователя."""
        tutor = seed_users["tutor"]
        response = await client.delete(f"/api/custom/users/{tutor.id}")
        assert response.status_code == 204

        # Проверяем, что удалён
        get_response = await client.get(f"/api/custom/users/{tutor.id}")
        assert get_response.status_code == 404


class TestTutorProfilesCRUD:
    """CRUD для /api/custom/tutor_profiles (UUID PK)."""

    @pytest.mark.asyncio
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

    @pytest.mark.asyncio
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
                "subject_id": seed_subjects[0].id,
                "hourly_rate": 60,
                "experience_years": 8,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["full_name"] == "Jane Smith"
        assert data["hourly_rate"] == 60

    @pytest.mark.asyncio
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

    @pytest.mark.asyncio
    async def test_get_tutor_profile_not_found(self, client: AsyncClient):
        """GET с несуществующим user_id — 404."""
        fake_id = uuid.uuid4()
        response = await client.get(f"/api/custom/tutor_profiles/{fake_id}")
        assert response.status_code == 404

    @pytest.mark.asyncio
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

    @pytest.mark.asyncio
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

    @pytest.mark.asyncio
    async def test_get_student_profile_not_found(self, client: AsyncClient):
        """GET /api/custom/student_profiles/{id} — 404 для несуществующего."""
        fake_id = uuid.uuid4()
        response = await client.get(f"/api/custom/student_profiles/{fake_id}")
        assert response.status_code == 404

    @pytest.mark.asyncio
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

    @pytest.mark.asyncio
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

    @pytest.mark.asyncio
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

    @pytest.mark.asyncio
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

    @pytest.mark.asyncio
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

    @pytest.mark.asyncio
    async def test_list_tutor_certifications(
        self, client: AsyncClient, seed_tutor_certification: TutorCertification
    ):
        """GET /api/custom/tutor_certifications — список сертификатов."""
        response = await client.get("/api/custom/tutor_certifications")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert data[0]["title"] == "Teaching Certificate"

    @pytest.mark.asyncio
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


class TestTutorTagsCompositePK:
    """Тесты для /api/custom/tutor_tags (составной PK)."""

    @pytest.mark.asyncio
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
                "tag_id": tag.id,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["tutor_id"] == str(tutor.id)
        assert data["tag_id"] == tag.id

    @pytest.mark.asyncio
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
                    "tag_id": tag.id,
                },
            )

        response = await client.get("/api/custom/tutor_tags")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    @pytest.mark.asyncio
    async def test_list_tutor_tags_filter_by_tutor(
        self, client: AsyncClient, seed_users: dict[str, User], seed_tags: list[Tag]
    ):
        """GET /api/custom/tutor_tags?tutor_id=... — фильтрация."""
        tutor = seed_users["tutor"]
        await client.post(
            "/api/custom/tutor_tags",
            json={
                "tutor_id": str(tutor.id),
                "tag_id": seed_tags[0].id,
            },
        )

        response = await client.get(f"/api/custom/tutor_tags?tutor_id={tutor.id}")
        assert response.status_code == 200
        assert len(response.json()) == 1

    @pytest.mark.asyncio
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
                "tag_id": tag.id,
            },
        )

        # Delete
        delete_resp = await client.delete(
            "/api/custom/tutor_tags",
            params={"tutor_id": str(tutor.id), "tag_id": tag.id},
        )
        assert delete_resp.status_code == 204

        # Проверяем что удалено
        list_resp = await client.get("/api/custom/tutor_tags")
        assert len(list_resp.json()) == 0


class TestStudentPreferredTagsCRUD:
    """CRUD для /api/custom/student_preferred_tags (составной PK)."""

    @pytest.mark.asyncio
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
                "tag_id": tag.id,
                "is_required": True,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["student_id"] == str(student.id)
        assert data["tag_id"] == tag.id
        assert data["is_required"] is True

    @pytest.mark.asyncio
    async def test_list_student_preferred_tags(
        self, client: AsyncClient, seed_student_preferred_tag: StudentPreferredTag
    ):
        """GET /api/custom/student_preferred_tags — список."""
        response = await client.get("/api/custom/student_preferred_tags")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    @pytest.mark.asyncio
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
                "tag_id": seed_tags[0].id,
            },
        )

        response = await client.get(
            f"/api/custom/student_preferred_tags?student_id={student.id}"
        )
        assert response.status_code == 200
        assert len(response.json()) == 1

    @pytest.mark.asyncio
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
                "tag_id": tag.id,
            },
        )

        delete_resp = await client.delete(
            "/api/custom/student_preferred_tags",
            params={"student_id": str(student.id), "tag_id": tag.id},
        )
        assert delete_resp.status_code == 204

        list_resp = await client.get("/api/custom/student_preferred_tags")
        assert len(list_resp.json()) == 0


class TestSchedulesCRUD:
    """CRUD для /api/custom/schedules."""

    @pytest.mark.asyncio
    async def test_create_schedule(
        self, client: AsyncClient, seed_users: dict[str, User]
    ):
        """POST /api/custom/schedules — создание расписания."""
        tutor = seed_users["tutor"]
        response = await client.post(
            "/api/custom/schedules",
            json={
                "tutor_id": str(tutor.id),
                "day_of_week": 1,
                "start_time": "09:00:00",
                "end_time": "17:00:00",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["day_of_week"] == 1
        assert data["start_time"] == "09:00:00"
        assert data["end_time"] == "17:00:00"

    @pytest.mark.asyncio
    async def test_list_schedules(
        self, client: AsyncClient, seed_users: dict[str, User]
    ):
        """GET /api/custom/schedules — список расписаний."""
        tutor = seed_users["tutor"]

        await client.post(
            "/api/custom/schedules",
            json={
                "tutor_id": str(tutor.id),
                "day_of_week": 2,
                "start_time": "10:00:00",
                "end_time": "18:00:00",
            },
        )

        response = await client.get("/api/custom/schedules")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["tutor_id"] == str(tutor.id)

    @pytest.mark.asyncio
    async def test_get_schedule_by_id(
        self, client: AsyncClient, seed_users: dict[str, User]
    ):
        """GET /api/custom/schedules/{id} — получение по ID."""
        tutor = seed_users["tutor"]
        create_resp = await client.post(
            "/api/custom/schedules",
            json={
                "tutor_id": str(tutor.id),
                "day_of_week": 3,
                "start_time": "09:00:00",
                "end_time": "17:00:00",
            },
        )
        schedule_id = create_resp.json()["id"]

        response = await client.get(f"/api/custom/schedules/{schedule_id}")
        assert response.status_code == 200
        assert response.json()["id"] == schedule_id

    @pytest.mark.asyncio
    async def test_update_schedule(
        self, client: AsyncClient, seed_users: dict[str, User]
    ):
        """PATCH /api/custom/schedules/{id} — обновление расписания."""
        tutor = seed_users["tutor"]
        create_resp = await client.post(
            "/api/custom/schedules",
            json={
                "tutor_id": str(tutor.id),
                "day_of_week": 1,
                "start_time": "09:00:00",
                "end_time": "17:00:00",
            },
        )
        schedule_id = create_resp.json()["id"]

        response = await client.patch(
            f"/api/custom/schedules/{schedule_id}",
            json={"start_time": "10:00:00"},
        )
        assert response.status_code == 200
        assert response.json()["start_time"] == "10:00:00"

    @pytest.mark.asyncio
    async def test_delete_schedule(
        self, client: AsyncClient, seed_users: dict[str, User]
    ):
        """DELETE /api/custom/schedules/{id} — удаление расписания."""
        tutor = seed_users["tutor"]
        create_resp = await client.post(
            "/api/custom/schedules",
            json={
                "tutor_id": str(tutor.id),
                "day_of_week": 1,
                "start_time": "09:00:00",
                "end_time": "17:00:00",
            },
        )
        schedule_id = create_resp.json()["id"]

        response = await client.delete(f"/api/custom/schedules/{schedule_id}")
        assert response.status_code == 204

        # Проверяем удаление
        get_resp = await client.get(f"/api/custom/schedules/{schedule_id}")
        assert get_resp.status_code == 404


class TestLessonsCRUD:
    """CRUD для /api/custom/lessons (UUID PK)."""

    @pytest.mark.asyncio
    async def test_create_and_get_lesson(
        self, client: AsyncClient, seed_users: dict[str, User]
    ):
        """POST + GET /api/custom/lessons — создание и получение урока."""
        tutor_id = seed_users["tutor"].id
        student_id = seed_users["student"].id
        now = datetime.now(timezone.utc)
        start = now.isoformat()
        end = now.replace(hour=now.hour + 1).isoformat()

        create_resp = await client.post(
            "/api/custom/lessons",
            json={
                "student_id": str(student_id),
                "tutor_id": str(tutor_id),
                "start_datetime": start,
                "end_datetime": end,
            },
        )
        assert create_resp.status_code == 201
        lesson_id = create_resp.json()["id"]
        assert create_resp.json()["status"] == "planned"

        get_resp = await client.get(f"/api/custom/lessons/{lesson_id}")
        assert get_resp.status_code == 200
        assert get_resp.json()["id"] == lesson_id

    @pytest.mark.asyncio
    async def test_get_lesson_not_found(self, client: AsyncClient):
        """GET /api/custom/lessons с несуществующим UUID — 404."""
        response = await client.get(f"/api/custom/lessons/{uuid.uuid4()}")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_list_lessons_with_filters(
        self, client: AsyncClient, seed_users: dict[str, User]
    ):
        """GET /api/custom/lessons?tutor_id=... — фильтрация уроков."""
        tutor_id = seed_users["tutor"].id
        student_id = seed_users["student"].id
        now = datetime.now(timezone.utc)

        for _ in range(2):
            await client.post(
                "/api/custom/lessons",
                json={
                    "student_id": str(student_id),
                    "tutor_id": str(tutor_id),
                    "start_datetime": now.isoformat(),
                    "end_datetime": now.replace(hour=now.hour + 1).isoformat(),
                },
            )

        response = await client.get(f"/api/custom/lessons?tutor_id={tutor_id}")
        assert response.status_code == 200
        assert len(response.json()) == 2

    @pytest.mark.asyncio
    async def test_update_lesson_status(
        self, client: AsyncClient, seed_users: dict[str, User]
    ):
        """PATCH /api/custom/lessons/{id} — обновление статуса урока."""
        tutor_id = seed_users["tutor"].id
        student_id = seed_users["student"].id
        now = datetime.now(timezone.utc)

        create_resp = await client.post(
            "/api/custom/lessons",
            json={
                "student_id": str(student_id),
                "tutor_id": str(tutor_id),
                "start_datetime": now.isoformat(),
                "end_datetime": now.replace(hour=now.hour + 1).isoformat(),
            },
        )
        lesson_id = create_resp.json()["id"]

        update_resp = await client.patch(
            f"/api/custom/lessons/{lesson_id}",
            json={"status": "completed"},
        )
        assert update_resp.status_code == 200
        assert update_resp.json()["status"] == "completed"

    @pytest.mark.asyncio
    async def test_delete_lesson(self, client: AsyncClient, seed_lesson: Lesson):
        """DELETE /api/custom/lessons/{id} — удаление урока."""
        response = await client.delete(f"/api/custom/lessons/{seed_lesson.id}")
        assert response.status_code == 204

        get_resp = await client.get(f"/api/custom/lessons/{seed_lesson.id}")
        assert get_resp.status_code == 404


class TestApplicationsCRUD:
    """CRUD для /api/custom/applications."""

    @pytest.mark.asyncio
    async def test_create_application(
        self, client: AsyncClient, seed_users: dict[str, User]
    ):
        """POST /api/custom/applications — создание заявки."""
        student_id = seed_users["student"].id
        tutor_id = seed_users["tutor"].id

        response = await client.post(
            "/api/custom/applications",
            json={
                "student_id": str(student_id),
                "tutor_id": str(tutor_id),
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "pending"
        assert data["student_id"] == str(student_id)
        assert data["tutor_id"] == str(tutor_id)

    @pytest.mark.asyncio
    async def test_list_applications(
        self, client: AsyncClient, seed_application: Application
    ):
        """GET /api/custom/applications — список заявок."""
        response = await client.get("/api/custom/applications")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert data[0]["status"] == "pending"

    @pytest.mark.asyncio
    async def test_get_application(
        self, client: AsyncClient, seed_application: Application
    ):
        """GET /api/custom/applications/{id} — получение заявки."""
        # Applications используют UUID PK, но get by id не реализован в CRUD
        # Проверяем через list с фильтрацией
        response = await client.get(
            f"/api/custom/applications?student_id={seed_application.student_id}"
        )
        assert response.status_code == 200
        assert len(response.json()) == 1

    @pytest.mark.asyncio
    async def test_accept_application_sets_responded_at(
        self, client: AsyncClient, seed_users: dict[str, User]
    ):
        """PATCH со status='accepted' должен установить responded_at."""
        student_id = seed_users["student"].id
        tutor_id = seed_users["tutor"].id

        create_resp = await client.post(
            "/api/custom/applications",
            json={
                "student_id": str(student_id),
                "tutor_id": str(tutor_id),
            },
        )
        app_id = create_resp.json()["id"]

        update_resp = await client.patch(
            f"/api/custom/applications/{app_id}",
            json={"status": "accepted"},
        )
        assert update_resp.status_code == 200
        data = update_resp.json()
        assert data["status"] == "accepted"
        assert data["responded_at"] is not None, "responded_at должен быть установлен"

    @pytest.mark.asyncio
    async def test_delete_application(
        self, client: AsyncClient, seed_application: Application
    ):
        """DELETE /api/custom/applications/{id} — удаление заявки."""
        response = await client.delete(
            f"/api/custom/applications/{seed_application.id}"
        )
        assert response.status_code == 204

        get_resp = await client.get(
            f"/api/custom/applications?student_id={seed_application.student_id}"
        )
        assert len(get_resp.json()) == 0


class TestChatsCRUD:
    """CRUD для /api/custom/chats."""

    @pytest.mark.asyncio
    async def test_list_chats(self, client: AsyncClient, seed_chat: Chat):
        """GET /api/custom/chats — список чатов."""
        response = await client.get("/api/custom/chats")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert "application_id" in data[0]
        assert "id" in data[0]

    @pytest.mark.asyncio
    async def test_list_chats_filter_by_application(
        self, client: AsyncClient, seed_chat: Chat
    ):
        """GET /api/custom/chats?application_id=... — фильтрация."""
        response = await client.get(
            f"/api/custom/chats?application_id={seed_chat.application_id}"
        )
        assert response.status_code == 200
        assert len(response.json()) == 1


class TestMessagesCRUD:
    """CRUD для /api/custom/messages."""

    @pytest.mark.asyncio
    async def test_create_message(
        self, client: AsyncClient, seed_chat: Chat, seed_users: dict[str, User]
    ):
        """POST /api/custom/messages — создание сообщения в существующем чате."""
        tutor = seed_users["tutor"]
        response = await client.post(
            "/api/custom/messages",
            json={
                "chat_id": str(seed_chat.id),
                "sender_id": str(tutor.id),
                "text": "Hello, this is a test message!",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["text"] == "Hello, this is a test message!"
        assert not data["is_read"]
        assert "created_at" in data

    @pytest.mark.asyncio
    async def test_list_messages(self, client: AsyncClient, seed_message: Message):
        """GET /api/custom/messages — список сообщений."""
        response = await client.get("/api/custom/messages")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    @pytest.mark.asyncio
    async def test_list_messages_filter_by_chat(
        self, client: AsyncClient, seed_message: Message
    ):
        """GET /api/custom/messages?chat_id=... — фильтрация по чату."""
        response = await client.get(
            f"/api/custom/messages?chat_id={seed_message.chat_id}"
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["text"] == "Hello, this is a test message!"

    @pytest.mark.asyncio
    async def test_update_message_mark_as_read(
        self, client: AsyncClient, seed_message: Message
    ):
        """PATCH /api/custom/messages/{id} — отметить как прочитанное."""
        response = await client.patch(
            f"/api/custom/messages/{seed_message.id}",
            json={"is_read": True},
        )
        assert response.status_code == 200
        assert response.json()["is_read"] is True

    @pytest.mark.asyncio
    async def test_message_validation_missing_text(self, client: AsyncClient):
        """POST с пустым text — ожидаем 422."""
        response = await client.post(
            "/api/custom/messages",
            json={
                "chat_id": str(uuid.uuid4()),
                "sender_id": str(uuid.uuid4()),
            },
        )
        assert response.status_code == 422


class TestTestLibraryCRUD:
    """CRUD для /api/custom/test_library."""

    @pytest.mark.asyncio
    async def test_create_test_library(
        self, client: AsyncClient, seed_subjects: list[Subject]
    ):
        """POST /api/custom/test_library — создание теста в библиотеке."""
        response = await client.post(
            "/api/custom/test_library",
            json={
                "subject_id": seed_subjects[0].id,
                "topic": "Algebra Basics",
                "questions_json": {"questions": [{"q": "2+2?", "a": "4"}]},
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["topic"] == "Algebra Basics"
        assert "id" in data

    @pytest.mark.asyncio
    async def test_list_test_library(
        self, client: AsyncClient, seed_test_library: TestLibrary
    ):
        """GET /api/custom/test_library — список тестов."""
        response = await client.get("/api/custom/test_library")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert data[0]["topic"] == "Algebra Basics"

    @pytest.mark.asyncio
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
        response = await client.get("/api/custom/test_library?subject_id=99999")
        assert len(response.json()) == 0


class TestStudentResultsCRUD:
    """CRUD для /api/custom/student_results."""

    @pytest.mark.asyncio
    async def test_create_student_result(
        self,
        client: AsyncClient,
        seed_users: dict[str, User],
        seed_test_library: TestLibrary,
    ):
        """POST /api/custom/student_results — создание результата."""
        student = seed_users["student"]
        tutor = seed_users["tutor"]
        response = await client.post(
            "/api/custom/student_results",
            json={
                "student_id": str(student.id),
                "tutor_id": str(tutor.id),
                "test_id": seed_test_library.id,
                "type": "initial_test",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["type"] == "initial_test"
        assert data["score"] is None
        assert data["completed_at"] is None

    @pytest.mark.asyncio
    async def test_list_student_results(
        self, client: AsyncClient, seed_student_result: StudentResult
    ):
        """GET /api/custom/student_results — список результатов."""
        response = await client.get("/api/custom/student_results")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    @pytest.mark.asyncio
    async def test_list_student_results_filter(
        self, client: AsyncClient, seed_student_result: StudentResult
    ):
        """GET /api/custom/student_results?student_id=... — фильтрация."""
        student_id = seed_student_result.student_id
        response = await client.get(
            f"/api/custom/student_results?student_id={student_id}"
        )
        assert response.status_code == 200
        assert len(response.json()) == 1

    @pytest.mark.asyncio
    async def test_update_student_result_score(
        self, client: AsyncClient, seed_student_result: StudentResult
    ):
        """PATCH /api/custom/student_results/{id} — обновление оценки."""
        from datetime import datetime, timezone

        response = await client.patch(
            f"/api/custom/student_results/{seed_student_result.id}",
            json={
                "score": 85.5,
                "completed_at": datetime.now(timezone.utc).isoformat(),
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert float(data["score"]) == 85.5
        assert data["completed_at"] is not None


class TestReviewsCRUD:
    """CRUD для /api/custom/reviews."""

    @pytest.mark.asyncio
    async def test_create_review(
        self, client: AsyncClient, seed_lesson: Lesson, seed_users: dict[str, User]
    ):
        """POST /api/custom/reviews — создание отзыва."""
        student = seed_users["student"]
        tutor = seed_users["tutor"]
        response = await client.post(
            "/api/custom/reviews",
            json={
                "student_id": str(student.id),
                "tutor_id": str(tutor.id),
                "lesson_id": str(seed_lesson.id),
                "communication_score": 5,
                "text": "Excellent tutor!",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["communication_score"] == 5
        assert data["text"] == "Excellent tutor!"

    @pytest.mark.asyncio
    async def test_list_reviews(self, client: AsyncClient, seed_review: Review):
        """GET /api/custom/reviews — список отзывов."""
        response = await client.get("/api/custom/reviews")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert data[0]["text"] == "Great tutor!"

    @pytest.mark.asyncio
    async def test_list_reviews_filter_by_tutor(
        self, client: AsyncClient, seed_review: Review
    ):
        """GET /api/custom/reviews?tutor_id=... — фильтрация."""
        tutor_id = seed_review.tutor_id
        response = await client.get(f"/api/custom/reviews?tutor_id={tutor_id}")
        assert response.status_code == 200
        assert len(response.json()) == 1

    @pytest.mark.asyncio
    async def test_create_review_invalid_score(
        self, client: AsyncClient, seed_users: dict[str, User]
    ):
        """POST с некорректным communication_score — 422."""
        student = seed_users["student"]
        tutor = seed_users["tutor"]
        response = await client.post(
            "/api/custom/reviews",
            json={
                "student_id": str(student.id),
                "tutor_id": str(tutor.id),
                "communication_score": 10,  # должно быть 1-5
            },
        )
        assert response.status_code == 422


class TestDeviceTokensCRUD:
    """CRUD для /api/custom/device_tokens."""

    @pytest.mark.asyncio
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

    @pytest.mark.asyncio
    async def test_list_device_tokens(
        self, client: AsyncClient, seed_device_token: DeviceToken
    ):
        """GET /api/custom/device_tokens — список токенов."""
        response = await client.get("/api/custom/device_tokens")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    @pytest.mark.asyncio
    async def test_list_device_tokens_filter(
        self, client: AsyncClient, seed_device_token: DeviceToken
    ):
        """GET /api/custom/device_tokens?user_id=... — фильтрация."""
        user_id = seed_device_token.user_id
        response = await client.get(f"/api/custom/device_tokens?user_id={user_id}")
        assert response.status_code == 200
        assert len(response.json()) == 1

    @pytest.mark.asyncio
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


# =========================================================================
# ЧАСТЬ 2. Пагинация и фильтрация
# =========================================================================


class TestPaginationAndFiltering:
    """Тесты пагинации и фильтрации."""

    @pytest.mark.asyncio
    async def test_limit_offset(
        self, client: AsyncClient, seed_subjects: list[Subject]
    ):
        """GET /api/custom/subjects?limit=2&offset=1 — пагинация."""
        response = await client.get("/api/custom/subjects?limit=2&offset=1")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    @pytest.mark.asyncio
    async def test_limit_max_value(
        self, client: AsyncClient, seed_subjects: list[Subject]
    ):
        """GET /api/custom/subjects?limit=1001 — лимит ограничен 1000."""
        response = await client.get("/api/custom/subjects?limit=1001")
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_negative_offset(self, client: AsyncClient):
        """GET с отрицательным offset — 422."""
        response = await client.get("/api/custom/subjects?offset=-1")
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_postgrest_style_filter(
        self, client: AsyncClient, seed_subjects: list[Subject]
    ):
        """GET с PostgREST-стилем фильтрации eq."""
        response = await client.get("/api/custom/subjects?name=eq.Mathematics")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Mathematics"


# =========================================================================
# ЧАСТЬ 3. Бизнес-логика / алгоритмические тесты
# =========================================================================


class TestSuggestionsEndpoint:
    """Тесты эндпоинта рекомендаций /api/custom/suggestions."""

    @pytest.mark.asyncio
    async def test_suggestions_returns_empty_when_no_tutors(
        self, client: AsyncClient, seed_subjects: list[Subject]
    ):
        """POST /api/custom/suggestions — пустой результат если нет репетиторов."""
        response = await client.post(
            "/api/custom/suggestions",
            json={
                "subject_id": seed_subjects[0].id,
            },
        )
        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
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
                "subject_id": seed_subjects[0].id,
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

    @pytest.mark.asyncio
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
                "subject_id": seed_subjects[0].id,
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

    @pytest.mark.asyncio
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
                "subject_id": seed_subjects[0].id,
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

    @pytest.mark.asyncio
    async def test_suggestions_invalid_subject(self, client: AsyncClient):
        """POST /api/custom/suggestions — несуществующий subject_id."""
        response = await client.post(
            "/api/custom/suggestions",
            json={
                "subject_id": 99999,
            },
        )
        assert response.status_code == 200
        assert response.json() == []


class TestInternalWebhook:
    """Тесты внутреннего webhook-эндпоинта /api/custom/internal/user-created."""

    @pytest.mark.asyncio
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

    @pytest.mark.asyncio
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

    @pytest.mark.asyncio
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

    @pytest.mark.asyncio
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

    @pytest.mark.asyncio
    async def test_user_created_missing_fields(self, client: AsyncClient):
        """POST без обязательных полей — 422 Validation Error."""
        response = await client.post(
            "/api/custom/internal/user-created",
            json={
                "userId": str(uuid.uuid4()),
            },
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
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
