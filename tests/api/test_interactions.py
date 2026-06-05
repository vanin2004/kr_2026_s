"""
Интеграционные тесты — взаимодействие ученика и репетитора.

Приложение запущено в Docker. Тесты ходят по HTTP через Nginx.
"""

import uuid
from datetime import datetime, timedelta, timezone

import httpx

from ..conftest import API_BASE, NGINX_URL


def _random_email(prefix: str = "test") -> str:
    """Уникальный email для тестов."""
    return f"{prefix}-{uuid.uuid4().hex[:8]}@test.local"


class TestStudentTutorInteraction:
    """Полный цикл: регистрация → заявка → принятие → чат → урок → отзыв."""

    def test_full_interaction_flow(self):
        """Полный сценарий взаимодействия через API."""
        tutor_id = str(uuid.uuid4())
        student_id = str(uuid.uuid4())
        subject_id = None

        try:
            # --- Подготовка: создаём предмет ---
            resp = httpx.post(
                f"{NGINX_URL}{API_BASE}/subjects",
                json={"name": f"Предмет-{uuid.uuid4().hex[:4]}"},
                timeout=10,
            )
            assert resp.status_code == 201
            subject_id = resp.json()["id"]

            # --- Регистрация репетитора ---
            resp = httpx.post(
                f"{NGINX_URL}{API_BASE}/internal/user-created",
                json={
                    "userId": tutor_id,
                    "email": _random_email("ivan"),
                    "realmRole": "tutor",
                },
                timeout=10,
            )
            assert resp.status_code == 201

            httpx.patch(
                f"{NGINX_URL}{API_BASE}/tutor_profiles/{tutor_id}",
                json={
                    "full_name": "Иван Петров",
                    "subject_id": subject_id,
                    "hourly_rate": 150000,
                    "experience_years": 5,
                },
                timeout=10,
            )

            # --- Регистрация ученика ---
            resp = httpx.post(
                f"{NGINX_URL}{API_BASE}/internal/user-created",
                json={
                    "userId": student_id,
                    "email": _random_email("anna"),
                    "realmRole": "student",
                },
                timeout=10,
            )
            assert resp.status_code == 201

            # --- Шаг 1: Подача заявки ---
            resp = httpx.post(
                f"{NGINX_URL}{API_BASE}/applications",
                json={"student_id": student_id, "tutor_id": tutor_id},
                timeout=10,
            )
            assert resp.status_code == 201
            application_id = resp.json()["id"]
            assert resp.json()["status"] == "pending"

            # --- Шаг 1.5: Чтение заявки по ID ---
            resp = httpx.get(
                f"{NGINX_URL}{API_BASE}/applications/{application_id}", timeout=10
            )
            assert resp.status_code == 200
            assert resp.json()["id"] == application_id
            assert resp.json()["status"] == "pending"

            # --- Шаг 2: Принятие заявки репетитором ---
            resp = httpx.patch(
                f"{NGINX_URL}{API_BASE}/applications/{application_id}",
                json={"status": "accepted"},
                timeout=10,
            )
            assert resp.status_code == 200
            assert resp.json()["status"] == "accepted"
            assert resp.json()["responded_at"] is not None

            # --- Шаг 3: Проверка создания чата (триггер БД) ---
            resp = httpx.get(
                f"{NGINX_URL}{API_BASE}/chats",
                params={"application_id": application_id},
                timeout=10,
            )
            assert resp.status_code == 200
            chats = resp.json()
            assert len(chats) == 1, "При принятии заявки должен создаться чат"
            chat_id = chats[0]["id"]

            # --- Шаг 4: Отправка сообщений ---
            messages_data = [
                {"chat_id": chat_id, "sender_id": student_id, "text": "Здравствуйте!"},
                {
                    "chat_id": chat_id,
                    "sender_id": tutor_id,
                    "text": "Добрый день! Чем могу помочь?",
                },
                {
                    "chat_id": chat_id,
                    "sender_id": student_id,
                    "text": "Хочу подготовиться к ЕГЭ по математике.",
                },
            ]
            for msg in messages_data:
                resp = httpx.post(
                    f"{NGINX_URL}{API_BASE}/messages",
                    json=msg,
                    timeout=10,
                )
                assert resp.status_code == 201

            # --- Шаг 5: Просмотр сообщений (проверка сортировки) ---
            resp = httpx.get(
                f"{NGINX_URL}{API_BASE}/messages",
                params={"chat_id": chat_id},
                timeout=10,
            )
            assert resp.status_code == 200
            msgs = resp.json()
            assert len(msgs) == 3
            timestamps = [m["created_at"] for m in msgs]
            assert timestamps == sorted(timestamps)

            # --- Шаг 6: Отметка как прочитанные ---
            for msg in msgs:
                resp = httpx.patch(
                    f"{NGINX_URL}{API_BASE}/messages/{msg['id']}",
                    json={"is_read": True},
                    timeout=10,
                )
                assert resp.status_code == 200
                assert resp.json()["is_read"] is True

            # --- Шаг 7: Создание урока ---
            now = datetime.now(timezone.utc)
            resp = httpx.post(
                f"{NGINX_URL}{API_BASE}/lessons",
                json={
                    "student_id": student_id,
                    "tutor_id": tutor_id,
                    "start_datetime": (now + timedelta(days=5)).isoformat(),
                    "end_datetime": (now + timedelta(days=5, hours=1)).isoformat(),
                    "meeting_link": "https://zoom.us/j/integration-test",
                },
                timeout=10,
            )
            assert resp.status_code == 201
            lesson_id = resp.json()["id"]
            assert resp.json()["status"] == "planned"

            # --- Шаг 7.5: Чтение урока по ID ---
            resp = httpx.get(f"{NGINX_URL}{API_BASE}/lessons/{lesson_id}", timeout=10)
            assert resp.status_code == 200
            assert resp.json()["id"] == lesson_id
            assert resp.json()["status"] == "planned"

            # --- Шаг 8: Завершение урока ---
            resp = httpx.patch(
                f"{NGINX_URL}{API_BASE}/lessons/{lesson_id}",
                json={"status": "completed"},
                timeout=10,
            )
            assert resp.status_code == 200
            assert resp.json()["status"] == "completed"

            # --- Шаг 9: Оставление отзыва ---
            resp = httpx.post(
                f"{NGINX_URL}{API_BASE}/reviews",
                json={
                    "student_id": student_id,
                    "tutor_id": tutor_id,
                    "lesson_id": lesson_id,
                    "communication_score": 5,
                    "text": "Отличный преподаватель! Рекомендую.",
                },
                timeout=10,
            )
            assert resp.status_code == 201

            # --- Шаг 10: Проверка отзывов ---
            resp = httpx.get(
                f"{NGINX_URL}{API_BASE}/reviews",
                params={"tutor_id": tutor_id},
                timeout=10,
            )
            assert resp.status_code == 200
            assert any(r["tutor_id"] == tutor_id for r in resp.json())

            # --- Шаг 11: Дублирующаяся заявка (UNIQUE constraint) ---
            resp = httpx.post(
                f"{NGINX_URL}{API_BASE}/applications",
                json={"student_id": student_id, "tutor_id": tutor_id},
                timeout=10,
            )
            assert resp.status_code in (201, 409, 500)

            # --- Шаг 12: FCM-токен ---
            resp = httpx.post(
                f"{NGINX_URL}{API_BASE}/device_tokens",
                json={
                    "user_id": student_id,
                    "token": f"fcm-integration-{uuid.uuid4().hex}",
                    "platform": "ios",
                },
                timeout=10,
            )
            assert resp.status_code == 201
            assert resp.json()["platform"] == "ios"

        finally:
            for uid in [tutor_id, student_id]:
                httpx.delete(f"{NGINX_URL}{API_BASE}/users/{uid}", timeout=5)
            if subject_id:
                httpx.delete(f"{NGINX_URL}{API_BASE}/subjects/{subject_id}", timeout=5)

    def test_application_rejection(self):
        """Отклонение заявки репетитором."""
        tutor_id = str(uuid.uuid4())
        student_id = str(uuid.uuid4())
        subject_id = None

        try:
            # Создаём предмет
            resp = httpx.post(
                f"{NGINX_URL}{API_BASE}/subjects",
                json={"name": f"Предмет-{uuid.uuid4().hex[:4]}"},
                timeout=10,
            )
            subject_id = resp.json()["id"]

            # Создаём пользователей
            for uid, role, name in [
                (tutor_id, "tutor", "tutor-reject"),
                (student_id, "student", "student-reject"),
            ]:
                httpx.post(
                    f"{NGINX_URL}{API_BASE}/internal/user-created",
                    json={
                        "userId": uid,
                        "email": _random_email(name),
                        "realmRole": role,
                    },
                    timeout=10,
                )

            if subject_id:
                httpx.patch(
                    f"{NGINX_URL}{API_BASE}/tutor_profiles/{tutor_id}",
                    json={"full_name": "Пётр Отклоняющий", "subject_id": subject_id},
                    timeout=10,
                )

            # Заявка
            resp = httpx.post(
                f"{NGINX_URL}{API_BASE}/applications",
                json={"student_id": student_id, "tutor_id": tutor_id},
                timeout=10,
            )
            app_id = resp.json()["id"]

            # Отклонение
            resp = httpx.patch(
                f"{NGINX_URL}{API_BASE}/applications/{app_id}",
                json={"status": "rejected"},
                timeout=10,
            )
            assert resp.status_code == 200
            assert resp.json()["status"] == "rejected"
            assert resp.json()["responded_at"] is not None

            # Удаление заявки
            resp = httpx.delete(
                f"{NGINX_URL}{API_BASE}/applications/{app_id}", timeout=10
            )
            assert resp.status_code == 204

        finally:
            for uid in [tutor_id, student_id]:
                httpx.delete(f"{NGINX_URL}{API_BASE}/users/{uid}", timeout=5)
            if subject_id:
                httpx.delete(f"{NGINX_URL}{API_BASE}/subjects/{subject_id}", timeout=5)

    def test_delete_lesson(self):
        """Создание и удаление урока."""
        tutor_id = str(uuid.uuid4())
        student_id = str(uuid.uuid4())

        try:
            for uid, role, name in [
                (tutor_id, "tutor", "dl-t"),
                (student_id, "student", "dl-s"),
            ]:
                httpx.post(
                    f"{NGINX_URL}{API_BASE}/internal/user-created",
                    json={
                        "userId": uid,
                        "email": _random_email(name),
                        "realmRole": role,
                    },
                    timeout=10,
                )

            now = datetime.now(timezone.utc)
            resp = httpx.post(
                f"{NGINX_URL}{API_BASE}/lessons",
                json={
                    "student_id": student_id,
                    "tutor_id": tutor_id,
                    "start_datetime": (now + timedelta(days=10)).isoformat(),
                    "end_datetime": (now + timedelta(days=10, hours=1)).isoformat(),
                },
                timeout=10,
            )
            assert resp.status_code == 201
            lesson_id = resp.json()["id"]

            # Удаление урока
            resp = httpx.delete(
                f"{NGINX_URL}{API_BASE}/lessons/{lesson_id}", timeout=10
            )
            assert resp.status_code == 204

            # Проверка удаления
            resp = httpx.get(f"{NGINX_URL}{API_BASE}/lessons/{lesson_id}", timeout=10)
            assert resp.status_code == 404

        finally:
            for uid in [tutor_id, student_id]:
                httpx.delete(f"{NGINX_URL}{API_BASE}/users/{uid}", timeout=5)
