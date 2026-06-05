"""
CRUD-тесты для взаимодействий: applications, chats, messages, reviews, student_results.
"""

import uuid

import pytest
from httpx import AsyncClient
from models.tables import (
    Application,
    Chat,
    Lesson,
    Message,
    Review,
    StudentResult,
    TestLibrary,
    User,
)

pytestmark = pytest.mark.asyncio


class TestApplicationsCRUD:
    """CRUD для /api/custom/applications."""

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

    async def test_list_applications(
        self, client: AsyncClient, seed_application: Application
    ):
        """GET /api/custom/applications — список заявок."""
        response = await client.get("/api/custom/applications")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert data[0]["status"] == "pending"

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

    async def test_list_chats(self, client: AsyncClient, seed_chat: Chat):
        """GET /api/custom/chats — список чатов."""
        response = await client.get("/api/custom/chats")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert "application_id" in data[0]
        assert "id" in data[0]

    async def test_list_chats_filter_by_application(
        self, client: AsyncClient, seed_chat: Chat
    ):
        """GET /api/custom/chats?application_id=... — фильтрация."""
        response = await client.get(
            f"/api/custom/chats?application_id={seed_chat.application_id}"
        )
        assert response.status_code == 200
        assert len(response.json()) == 1

    async def test_get_chat(self, client: AsyncClient, seed_chat: Chat):
        """GET /api/custom/chats/{chat_id} — получение чата по ID."""
        response = await client.get(f"/api/custom/chats/{seed_chat.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(seed_chat.id)
        assert data["application_id"] == str(seed_chat.application_id)

    async def test_get_chat_not_found(self, client: AsyncClient):
        """GET /api/custom/chats с несуществующим UUID — 404."""
        response = await client.get(f"/api/custom/chats/{uuid.uuid4()}")
        assert response.status_code == 404


class TestMessagesCRUD:
    """CRUD для /api/custom/messages."""

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

    async def test_list_messages(self, client: AsyncClient, seed_message: Message):
        """GET /api/custom/messages — список сообщений."""
        response = await client.get("/api/custom/messages")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

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

    async def test_get_message(self, client: AsyncClient, seed_message: Message):
        """GET /api/custom/messages/{id} — получение сообщения по ID."""
        response = await client.get(f"/api/custom/messages/{seed_message.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(seed_message.id)
        assert data["text"] == "Hello, this is a test message!"

    async def test_get_message_not_found(self, client: AsyncClient):
        """GET /api/custom/messages с несуществующим UUID — 404."""
        response = await client.get(f"/api/custom/messages/{uuid.uuid4()}")
        assert response.status_code == 404

    async def test_delete_message(self, client: AsyncClient, seed_message: Message):
        """DELETE /api/custom/messages/{id} — удаление сообщения."""
        response = await client.delete(f"/api/custom/messages/{seed_message.id}")
        assert response.status_code == 204

        # Проверяем удаление
        get_resp = await client.get(f"/api/custom/messages/{seed_message.id}")
        assert get_resp.status_code == 404


class TestStudentResultsCRUD:
    """CRUD для /api/custom/student_results."""

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
                "test_id": str(seed_test_library.id),
                "type": "initial_test",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["type"] == "initial_test"
        assert data["score"] is None
        assert data["completed_at"] is None

    async def test_list_student_results(
        self, client: AsyncClient, seed_student_result: StudentResult
    ):
        """GET /api/custom/student_results — список результатов."""
        response = await client.get("/api/custom/student_results")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

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

    async def test_get_student_result(
        self, client: AsyncClient, seed_student_result: StudentResult
    ):
        """GET /api/custom/student_results/{id} — получение результата по ID."""
        result_id = seed_student_result.id
        response = await client.get(f"/api/custom/student_results/{result_id}")
        assert response.status_code == 200
        assert response.json()["id"] == str(result_id)
        assert response.json()["type"] == "initial_test"

    async def test_get_student_result_not_found(self, client: AsyncClient):
        """GET с несуществующим UUID — 404."""
        response = await client.get(f"/api/custom/student_results/{uuid.uuid4()}")
        assert response.status_code == 404

    async def test_delete_student_result(
        self, client: AsyncClient, seed_student_result: StudentResult
    ):
        """DELETE /api/custom/student_results/{id} — удаление результата."""
        result_id = seed_student_result.id
        response = await client.delete(f"/api/custom/student_results/{result_id}")
        assert response.status_code == 204

        # Проверяем удаление
        get_resp = await client.get(f"/api/custom/student_results/{result_id}")
        assert get_resp.status_code == 404


class TestReviewsCRUD:
    """CRUD для /api/custom/reviews."""

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

    async def test_list_reviews(self, client: AsyncClient, seed_review: Review):
        """GET /api/custom/reviews — список отзывов."""
        response = await client.get("/api/custom/reviews")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert data[0]["text"] == "Great tutor!"

    async def test_list_reviews_filter_by_tutor(
        self, client: AsyncClient, seed_review: Review
    ):
        """GET /api/custom/reviews?tutor_id=... — фильтрация."""
        tutor_id = seed_review.tutor_id
        response = await client.get(f"/api/custom/reviews?tutor_id={tutor_id}")
        assert response.status_code == 200
        assert len(response.json()) == 1

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

    async def test_get_review(self, client: AsyncClient, seed_review: Review):
        """GET /api/custom/reviews/{id} — получение отзыва по ID."""
        response = await client.get(f"/api/custom/reviews/{seed_review.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(seed_review.id)
        assert data["text"] == "Great tutor!"

    async def test_get_review_not_found(self, client: AsyncClient):
        """GET с несуществующим UUID — 404."""
        response = await client.get(f"/api/custom/reviews/{uuid.uuid4()}")
        assert response.status_code == 404

    async def test_update_review(self, client: AsyncClient, seed_review: Review):
        """PATCH /api/custom/reviews/{id} — обновление отзыва."""
        response = await client.patch(
            f"/api/custom/reviews/{seed_review.id}",
            json={"communication_score": 4, "text": "Updated review text"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["communication_score"] == 4
        assert data["text"] == "Updated review text"

    async def test_delete_review(self, client: AsyncClient, seed_review: Review):
        """DELETE /api/custom/reviews/{id} — удаление отзыва."""
        response = await client.delete(f"/api/custom/reviews/{seed_review.id}")
        assert response.status_code == 204

        # Проверяем удаление
        get_resp = await client.get(f"/api/custom/reviews/{seed_review.id}")
        assert get_resp.status_code == 404
