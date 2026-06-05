"""
Интеграционные тесты — новые эндпоинты (get/update/delete по ID).

Проверяет эндпоинты, добавленные для полного CRUD-покрытия:
student_profiles, tutor_certifications, chats, messages,
test_library, student_results, reviews, device_tokens.

Приложение запущено в Docker. Тесты ходят по HTTP через Nginx.
"""

import uuid

import httpx

from ..conftest import API_BASE, NGINX_URL


def _random_email(prefix: str = "test") -> str:
    """Уникальный email для тестов."""
    return f"{prefix}-{uuid.uuid4().hex[:8]}@test.local"


def _create_user(user_id: str, email: str, role: str):
    """Создать пользователя через webhook."""
    httpx.post(
        f"{NGINX_URL}{API_BASE}/internal/user-created",
        json={"userId": user_id, "email": email, "realmRole": role},
        timeout=10,
    )


class TestStudentProfilesExtended:
    """Список и удаление профилей учеников."""

    def test_student_profiles_list(self):
        """GET /api/custom/student_profiles — список профилей."""
        student_id = str(uuid.uuid4())
        try:
            _create_user(student_id, _random_email("spl"), "student")

            # Создаём профиль
            httpx.post(
                f"{NGINX_URL}{API_BASE}/student_profiles",
                json={"user_id": student_id, "full_name": "Студент Для Списка"},
                timeout=10,
            )

            # Список профилей
            resp = httpx.get(f"{NGINX_URL}{API_BASE}/student_profiles", timeout=10)
            assert resp.status_code == 200
            assert any(p["user_id"] == student_id for p in resp.json())

        finally:
            httpx.delete(f"{NGINX_URL}{API_BASE}/users/{student_id}", timeout=5)

    def test_student_profile_delete(self):
        """DELETE /api/custom/student_profiles/{id} — удаление профиля."""
        student_id = str(uuid.uuid4())
        try:
            _create_user(student_id, _random_email("spd"), "student")

            httpx.post(
                f"{NGINX_URL}{API_BASE}/student_profiles",
                json={"user_id": student_id, "full_name": "На Удаление"},
                timeout=10,
            )

            resp = httpx.delete(
                f"{NGINX_URL}{API_BASE}/student_profiles/{student_id}", timeout=10
            )
            assert resp.status_code == 204

            # Проверяем удаление
            resp = httpx.get(
                f"{NGINX_URL}{API_BASE}/student_profiles/{student_id}", timeout=10
            )
            assert resp.status_code == 404

        finally:
            httpx.delete(f"{NGINX_URL}{API_BASE}/users/{student_id}", timeout=5)


class TestTutorCertificationsExtended:
    """GET/PATCH/DELETE сертификатов по ID."""

    def test_tutor_certification_crud_by_id(self):
        """Полный цикл: create → get → update → delete."""
        tutor_id = str(uuid.uuid4())
        try:
            _create_user(tutor_id, _random_email("tce"), "tutor")

            # Create
            resp = httpx.post(
                f"{NGINX_URL}{API_BASE}/tutor_certifications",
                json={
                    "tutor_id": tutor_id,
                    "title": "Сертификат Для Теста",
                    "file_url": "https://example.com/test.pdf",
                },
                timeout=10,
            )
            assert resp.status_code == 201
            cert_id = resp.json()["id"]

            # GET by ID
            resp = httpx.get(
                f"{NGINX_URL}{API_BASE}/tutor_certifications/{cert_id}", timeout=10
            )
            assert resp.status_code == 200
            assert resp.json()["title"] == "Сертификат Для Теста"
            assert resp.json()["is_verified"] is False

            # PATCH — подтвердить
            resp = httpx.patch(
                f"{NGINX_URL}{API_BASE}/tutor_certifications/{cert_id}",
                json={"is_verified": True},
                timeout=10,
            )
            assert resp.status_code == 200
            assert resp.json()["is_verified"] is True

            # DELETE
            resp = httpx.delete(
                f"{NGINX_URL}{API_BASE}/tutor_certifications/{cert_id}", timeout=10
            )
            assert resp.status_code == 204

            # Проверяем удаление
            resp = httpx.get(
                f"{NGINX_URL}{API_BASE}/tutor_certifications/{cert_id}", timeout=10
            )
            assert resp.status_code == 404

        finally:
            httpx.delete(f"{NGINX_URL}{API_BASE}/users/{tutor_id}", timeout=5)

    def test_tutor_certification_not_found(self):
        """GET несуществующего сертификата — 404."""
        resp = httpx.get(
            f"{NGINX_URL}{API_BASE}/tutor_certifications/999999", timeout=10
        )
        assert resp.status_code == 404


class TestChatsExtended:
    """GET чата по ID."""

    def test_get_chat_by_id(self):
        """GET /api/custom/chats/{id} — получение чата."""
        tutor_id = str(uuid.uuid4())
        student_id = str(uuid.uuid4())
        subject_id = None

        try:
            # Создаём предмет
            resp = httpx.post(
                f"{NGINX_URL}{API_BASE}/subjects",
                json={"name": f"чат-предмет-{uuid.uuid4().hex[:4]}"},
                timeout=10,
            )
            subject_id = resp.json()["id"]

            for uid, role in [(tutor_id, "tutor"), (student_id, "student")]:
                _create_user(uid, _random_email(f"ch-{role}"), role)

            # Заявка → принятие → чат
            resp = httpx.post(
                f"{NGINX_URL}{API_BASE}/applications",
                json={"student_id": student_id, "tutor_id": tutor_id},
                timeout=10,
            )
            app_id = resp.json()["id"]

            httpx.patch(
                f"{NGINX_URL}{API_BASE}/applications/{app_id}",
                json={"status": "accepted"},
                timeout=10,
            )

            # Находим chat_id
            resp = httpx.get(
                f"{NGINX_URL}{API_BASE}/chats",
                params={"application_id": app_id},
                timeout=10,
            )
            chat_id = resp.json()[0]["id"]

            # GET чата по ID
            resp = httpx.get(f"{NGINX_URL}{API_BASE}/chats/{chat_id}", timeout=10)
            assert resp.status_code == 200
            assert resp.json()["id"] == chat_id
            assert resp.json()["application_id"] == app_id

        finally:
            for uid in [tutor_id, student_id]:
                httpx.delete(f"{NGINX_URL}{API_BASE}/users/{uid}", timeout=5)
            if subject_id:
                httpx.delete(f"{NGINX_URL}{API_BASE}/subjects/{subject_id}", timeout=5)


class TestMessagesExtended:
    """GET и DELETE сообщений."""

    def test_get_and_delete_message(self):
        """GET + DELETE /api/custom/messages/{id}."""
        tutor_id = str(uuid.uuid4())
        student_id = str(uuid.uuid4())
        subject_id = None

        try:
            resp = httpx.post(
                f"{NGINX_URL}{API_BASE}/subjects",
                json={"name": f"msg-предмет-{uuid.uuid4().hex[:4]}"},
                timeout=10,
            )
            subject_id = resp.json()["id"]

            for uid, role in [(tutor_id, "tutor"), (student_id, "student")]:
                _create_user(uid, _random_email(f"msg-{role}"), role)

            # Заявка → принятие → чат
            resp = httpx.post(
                f"{NGINX_URL}{API_BASE}/applications",
                json={"student_id": student_id, "tutor_id": tutor_id},
                timeout=10,
            )
            app_id = resp.json()["id"]

            httpx.patch(
                f"{NGINX_URL}{API_BASE}/applications/{app_id}",
                json={"status": "accepted"},
                timeout=10,
            )

            resp = httpx.get(
                f"{NGINX_URL}{API_BASE}/chats",
                params={"application_id": app_id},
                timeout=10,
            )
            chat_id = resp.json()[0]["id"]

            # Создаём сообщение
            resp = httpx.post(
                f"{NGINX_URL}{API_BASE}/messages",
                json={
                    "chat_id": chat_id,
                    "sender_id": student_id,
                    "text": "Тестовое сообщение!",
                },
                timeout=10,
            )
            assert resp.status_code == 201
            msg_id = resp.json()["id"]

            # GET by ID
            resp = httpx.get(f"{NGINX_URL}{API_BASE}/messages/{msg_id}", timeout=10)
            assert resp.status_code == 200
            assert resp.json()["text"] == "Тестовое сообщение!"

            # DELETE
            resp = httpx.delete(f"{NGINX_URL}{API_BASE}/messages/{msg_id}", timeout=10)
            assert resp.status_code == 204

            # Проверяем удаление
            resp = httpx.get(f"{NGINX_URL}{API_BASE}/messages/{msg_id}", timeout=10)
            assert resp.status_code == 404

        finally:
            for uid in [tutor_id, student_id]:
                httpx.delete(f"{NGINX_URL}{API_BASE}/users/{uid}", timeout=5)
            if subject_id:
                httpx.delete(f"{NGINX_URL}{API_BASE}/subjects/{subject_id}", timeout=5)


class TestTestLibraryExtended:
    """GET/PATCH/DELETE тестов по ID."""

    def test_test_library_crud_by_id(self):
        """Полный цикл: create → get → update → delete."""
        subject_id = None
        try:
            resp = httpx.post(
                f"{NGINX_URL}{API_BASE}/subjects",
                json={"name": f"tl-предмет-{uuid.uuid4().hex[:4]}"},
                timeout=10,
            )
            subject_id = resp.json()["id"]

            # Create
            resp = httpx.post(
                f"{NGINX_URL}{API_BASE}/test_library",
                json={
                    "subject_id": subject_id,
                    "topic": "Интеграционный тест",
                    "questions_json": {"q": [{"q": "1+1?", "a": "2"}]},
                },
                timeout=10,
            )
            assert resp.status_code == 201
            test_id = resp.json()["id"]

            # GET by ID
            resp = httpx.get(
                f"{NGINX_URL}{API_BASE}/test_library/{test_id}", timeout=10
            )
            assert resp.status_code == 200
            assert resp.json()["topic"] == "Интеграционный тест"

            # PATCH
            resp = httpx.patch(
                f"{NGINX_URL}{API_BASE}/test_library/{test_id}",
                json={"topic": "Обновлённый тест"},
                timeout=10,
            )
            assert resp.status_code == 200
            assert resp.json()["topic"] == "Обновлённый тест"

            # DELETE
            resp = httpx.delete(
                f"{NGINX_URL}{API_BASE}/test_library/{test_id}", timeout=10
            )
            assert resp.status_code == 204

            # Проверяем удаление
            resp = httpx.get(
                f"{NGINX_URL}{API_BASE}/test_library/{test_id}", timeout=10
            )
            assert resp.status_code == 404

        finally:
            if subject_id:
                httpx.delete(f"{NGINX_URL}{API_BASE}/subjects/{subject_id}", timeout=5)


class TestStudentResultsExtended:
    """GET и DELETE результатов по ID."""

    def test_student_result_get_and_delete(self):
        """GET + DELETE /api/custom/student_results/{id}."""
        tutor_id = str(uuid.uuid4())
        student_id = str(uuid.uuid4())
        subject_id = None

        try:
            resp = httpx.post(
                f"{NGINX_URL}{API_BASE}/subjects",
                json={"name": f"sr-предмет-{uuid.uuid4().hex[:4]}"},
                timeout=10,
            )
            subject_id = resp.json()["id"]

            for uid, role in [(tutor_id, "tutor"), (student_id, "student")]:
                _create_user(uid, _random_email(f"sr-{role}"), role)

            # Создаём тест
            resp = httpx.post(
                f"{NGINX_URL}{API_BASE}/test_library",
                json={
                    "subject_id": subject_id,
                    "topic": "Результат-тест",
                    "questions_json": {},
                },
                timeout=10,
            )
            test_id = resp.json()["id"]

            # Создаём результат
            resp = httpx.post(
                f"{NGINX_URL}{API_BASE}/student_results",
                json={
                    "student_id": student_id,
                    "tutor_id": tutor_id,
                    "test_id": test_id,
                    "type": "initial_test",
                },
                timeout=10,
            )
            assert resp.status_code == 201
            result_id = resp.json()["id"]

            # GET by ID
            resp = httpx.get(
                f"{NGINX_URL}{API_BASE}/student_results/{result_id}", timeout=10
            )
            assert resp.status_code == 200
            assert resp.json()["id"] == result_id
            assert resp.json()["type"] == "initial_test"

            # DELETE
            resp = httpx.delete(
                f"{NGINX_URL}{API_BASE}/student_results/{result_id}", timeout=10
            )
            assert resp.status_code == 204

            # Проверяем удаление
            resp = httpx.get(
                f"{NGINX_URL}{API_BASE}/student_results/{result_id}", timeout=10
            )
            assert resp.status_code == 404

        finally:
            for uid in [tutor_id, student_id]:
                httpx.delete(f"{NGINX_URL}{API_BASE}/users/{uid}", timeout=5)
            if subject_id:
                httpx.delete(f"{NGINX_URL}{API_BASE}/subjects/{subject_id}", timeout=5)


class TestReviewsExtended:
    """GET/PATCH/DELETE отзывов по ID."""

    def test_review_crud_by_id(self):
        """Полный цикл: create → get → update → delete."""
        tutor_id = str(uuid.uuid4())
        student_id = str(uuid.uuid4())
        subject_id = None

        try:
            resp = httpx.post(
                f"{NGINX_URL}{API_BASE}/subjects",
                json={"name": f"rev-предмет-{uuid.uuid4().hex[:4]}"},
                timeout=10,
            )
            subject_id = resp.json()["id"]

            for uid, role in [(tutor_id, "tutor"), (student_id, "student")]:
                _create_user(uid, _random_email(f"rev-{role}"), role)

            # Создаём урок
            from datetime import datetime, timedelta, timezone

            now = datetime.now(timezone.utc)
            resp = httpx.post(
                f"{NGINX_URL}{API_BASE}/lessons",
                json={
                    "student_id": student_id,
                    "tutor_id": tutor_id,
                    "start_datetime": (now + timedelta(days=1)).isoformat(),
                    "end_datetime": (now + timedelta(days=1, hours=1)).isoformat(),
                },
                timeout=10,
            )
            lesson_id = resp.json()["id"]

            # Создаём отзыв
            resp = httpx.post(
                f"{NGINX_URL}{API_BASE}/reviews",
                json={
                    "student_id": student_id,
                    "tutor_id": tutor_id,
                    "lesson_id": lesson_id,
                    "communication_score": 5,
                    "text": "Отличный преподаватель!",
                },
                timeout=10,
            )
            assert resp.status_code == 201
            review_id = resp.json()["id"]

            # GET by ID
            resp = httpx.get(f"{NGINX_URL}{API_BASE}/reviews/{review_id}", timeout=10)
            assert resp.status_code == 200
            assert resp.json()["communication_score"] == 5
            assert resp.json()["text"] == "Отличный преподаватель!"

            # PATCH
            resp = httpx.patch(
                f"{NGINX_URL}{API_BASE}/reviews/{review_id}",
                json={"communication_score": 4, "text": "Хороший преподаватель!"},
                timeout=10,
            )
            assert resp.status_code == 200
            assert resp.json()["communication_score"] == 4
            assert resp.json()["text"] == "Хороший преподаватель!"

            # DELETE
            resp = httpx.delete(
                f"{NGINX_URL}{API_BASE}/reviews/{review_id}", timeout=10
            )
            assert resp.status_code == 204

            # Проверяем удаление
            resp = httpx.get(f"{NGINX_URL}{API_BASE}/reviews/{review_id}", timeout=10)
            assert resp.status_code == 404

        finally:
            for uid in [tutor_id, student_id]:
                httpx.delete(f"{NGINX_URL}{API_BASE}/users/{uid}", timeout=5)
            if subject_id:
                httpx.delete(f"{NGINX_URL}{API_BASE}/subjects/{subject_id}", timeout=5)


class TestDeviceTokensExtended:
    """GET токена устройства по ID."""

    def test_get_device_token_by_id(self):
        """GET /api/custom/device_tokens/{id}."""
        user_id = str(uuid.uuid4())
        try:
            _create_user(user_id, _random_email("dtg"), "student")

            resp = httpx.post(
                f"{NGINX_URL}{API_BASE}/device_tokens",
                json={
                    "user_id": user_id,
                    "token": f"fcm-int-get-{uuid.uuid4().hex}",
                    "platform": "ios",
                },
                timeout=10,
            )
            assert resp.status_code == 201
            token_id = resp.json()["id"]

            # GET by ID
            resp = httpx.get(
                f"{NGINX_URL}{API_BASE}/device_tokens/{token_id}", timeout=10
            )
            assert resp.status_code == 200
            assert resp.json()["id"] == token_id
            assert resp.json()["platform"] == "ios"

        finally:
            httpx.delete(f"{NGINX_URL}{API_BASE}/users/{user_id}", timeout=5)

    def test_get_device_token_not_found(self):
        """GET несуществующего токена — 404."""
        resp = httpx.get(f"{NGINX_URL}{API_BASE}/device_tokens/999999", timeout=10)
        assert resp.status_code == 404
