"""
Интеграционные тесты — фильтрация, пагинация, edge cases и валидация.

Приложение запущено в Docker. Тесты ходят по HTTP через Nginx.
"""

import uuid
from datetime import datetime, timedelta, timezone

import httpx

from ..conftest import API_BASE, NGINX_URL


def _random_email(prefix: str = "test") -> str:
    """Уникальный email для тестов."""
    return f"{prefix}-{uuid.uuid4().hex[:8]}@test.local"


class TestFilteringAndPagination:
    """Проверка query-параметров: limit, offset, фильтрация."""

    def test_list_endpoints_return_lists(self):
        """Базовые эндпоинты возвращают списки (не ошибки)."""
        endpoints = [
            "/subjects",
            "/tags",
            "/users",
            "/tutor_profiles",
            "/lessons",
            "/applications",
            "/chats",
            "/messages",
            "/test_library",
            "/student_results",
            "/reviews",
            "/device_tokens",
        ]
        for ep in endpoints:
            resp = httpx.get(f"{NGINX_URL}{API_BASE}{ep}", timeout=10)
            assert resp.status_code == 200
            assert isinstance(resp.json(), list), f"{ep} должен возвращать список"

    def test_nonexistent_routes(self):
        """Несуществующие маршруты."""
        resp = httpx.get(f"{NGINX_URL}/api/custom/nonexistent", timeout=10)
        assert resp.status_code == 404

        resp = httpx.get(f"{NGINX_URL}/nonexistent", timeout=10)
        assert resp.status_code == 404


class TestValidation:
    """Проверка валидации на краевых случаях."""

    def test_lesson_past_date(self):
        """Урок в прошлом (API не валидирует, но проверяем формат дат)."""
        tutor_id = str(uuid.uuid4())
        student_id = str(uuid.uuid4())

        try:
            for uid, role, name in [
                (tutor_id, "tutor", "vl-t"),
                (student_id, "student", "vl-s"),
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

            past = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
            resp = httpx.post(
                f"{NGINX_URL}{API_BASE}/lessons",
                json={
                    "student_id": student_id,
                    "tutor_id": tutor_id,
                    "start_datetime": past,
                    "end_datetime": past,
                },
                timeout=10,
            )
            # API принимает любую дату (нет валидации в бизнес-логике)
            assert resp.status_code == 201

        finally:
            for uid in [tutor_id, student_id]:
                httpx.delete(f"{NGINX_URL}{API_BASE}/users/{uid}", timeout=5)

    def test_student_preferred_tags(self):
        """Предпочитаемые теги ученика: создание, список, удаление."""
        student_id = str(uuid.uuid4())
        tag_ids = []

        try:
            httpx.post(
                f"{NGINX_URL}{API_BASE}/internal/user-created",
                json={
                    "userId": student_id,
                    "email": _random_email("spt"),
                    "realmRole": "student",
                },
                timeout=10,
            )

            # Создаём теги
            for _ in range(3):
                resp = httpx.post(
                    f"{NGINX_URL}{API_BASE}/tags",
                    json={"name": f"pref-{uuid.uuid4().hex[:4]}"},
                    timeout=10,
                )
                tag_ids.append(resp.json()["id"])

            # Добавляем предпочитаемые теги
            for tag_id in tag_ids:
                resp = httpx.post(
                    f"{NGINX_URL}{API_BASE}/student_preferred_tags",
                    json={
                        "student_id": student_id,
                        "tag_id": tag_id,
                        "is_required": tag_id == tag_ids[0],
                    },
                    timeout=10,
                )
                assert resp.status_code == 201

            # Получаем список
            resp = httpx.get(
                f"{NGINX_URL}{API_BASE}/student_preferred_tags",
                params={"student_id": student_id},
                timeout=10,
            )
            assert resp.status_code == 200
            assert len(resp.json()) == 3

            # Удаляем все теги
            for tag_id in tag_ids:
                httpx.delete(
                    f"{NGINX_URL}{API_BASE}/student_preferred_tags",
                    params={"student_id": student_id, "tag_id": tag_id},
                    timeout=10,
                )

            # Список пуст
            resp = httpx.get(
                f"{NGINX_URL}{API_BASE}/student_preferred_tags",
                params={"student_id": student_id},
                timeout=10,
            )
            assert len(resp.json()) == 0

        finally:
            httpx.delete(f"{NGINX_URL}{API_BASE}/users/{student_id}", timeout=5)
            for tag_id in tag_ids:
                httpx.delete(f"{NGINX_URL}{API_BASE}/tags/{tag_id}", timeout=5)
