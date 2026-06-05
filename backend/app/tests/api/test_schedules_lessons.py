"""
CRUD-тесты для schedules и lessons.
"""

import uuid
from datetime import datetime, timezone

import pytest
from httpx import AsyncClient
from models.tables import Lesson, User

pytestmark = pytest.mark.asyncio


class TestSchedulesCRUD:
    """CRUD для /api/custom/schedules."""

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

    async def test_get_lesson_not_found(self, client: AsyncClient):
        """GET /api/custom/lessons с несуществующим UUID — 404."""
        response = await client.get(f"/api/custom/lessons/{uuid.uuid4()}")
        assert response.status_code == 404

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

    async def test_delete_lesson(self, client: AsyncClient, seed_lesson: Lesson):
        """DELETE /api/custom/lessons/{id} — удаление урока."""
        response = await client.delete(f"/api/custom/lessons/{seed_lesson.id}")
        assert response.status_code == 204

        get_resp = await client.get(f"/api/custom/lessons/{seed_lesson.id}")
        assert get_resp.status_code == 404
