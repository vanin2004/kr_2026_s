"""
Интеграционные тесты — полный цикл настройки репетитора.

Приложение запущено в Docker. Тесты ходят по HTTP через Nginx.
"""

import uuid
from datetime import datetime, timedelta, timezone

import httpx

from ..conftest import API_BASE, NGINX_URL


def _random_email(prefix: str = "test") -> str:
    """Уникальный email для тестов."""
    return f"{prefix}-{uuid.uuid4().hex[:8]}@test.local"


class TestTutorFullSetup:
    """Теги, расписание, сертификаты репетитора."""

    def test_tutor_tags(self):
        """Добавление, список и удаление тегов репетитора."""
        tutor_id = str(uuid.uuid4())
        email = _random_email("tt")

        try:
            # Создаём репетитора
            httpx.post(
                f"{NGINX_URL}{API_BASE}/internal/user-created",
                json={"userId": tutor_id, "email": email, "realmRole": "tutor"},
                timeout=10,
            )

            # Создаём теги в справочнике
            tag_ids = []
            for _ in range(3):
                resp = httpx.post(
                    f"{NGINX_URL}{API_BASE}/tags",
                    json={"name": f"тег-{uuid.uuid4().hex[:4]}"},
                    timeout=10,
                )
                assert resp.status_code == 201
                tag_ids.append(resp.json()["id"])

            # Добавляем теги репетитору
            for tag_id in tag_ids:
                resp = httpx.post(
                    f"{NGINX_URL}{API_BASE}/tutor_tags",
                    json={"tutor_id": tutor_id, "tag_id": tag_id},
                    timeout=10,
                )
                assert resp.status_code == 201

            # Список тегов репетитора
            resp = httpx.get(
                f"{NGINX_URL}{API_BASE}/tutor_tags",
                params={"tutor_id": tutor_id},
                timeout=10,
            )
            assert resp.status_code == 200
            assert len(resp.json()) == 3

            # Удаляем один тег
            resp = httpx.delete(
                f"{NGINX_URL}{API_BASE}/tutor_tags",
                params={"tutor_id": tutor_id, "tag_id": tag_ids[0]},
                timeout=10,
            )
            assert resp.status_code == 204

            # Проверяем: осталось 2
            resp = httpx.get(
                f"{NGINX_URL}{API_BASE}/tutor_tags",
                params={"tutor_id": tutor_id},
                timeout=10,
            )
            assert len(resp.json()) == 2

            # Удаляем оставшиеся
            for tag_id in tag_ids[1:]:
                httpx.delete(
                    f"{NGINX_URL}{API_BASE}/tutor_tags",
                    params={"tutor_id": tutor_id, "tag_id": tag_id},
                    timeout=10,
                )

            # Очищаем справочник тегов
            for tag_id in tag_ids:
                httpx.delete(f"{NGINX_URL}{API_BASE}/tags/{tag_id}", timeout=10)

        finally:
            httpx.delete(f"{NGINX_URL}{API_BASE}/users/{tutor_id}", timeout=5)

    def test_tutor_schedules(self):
        """Расписание: создание регулярных слотов, обновление, удаление."""
        tutor_id = str(uuid.uuid4())
        email = _random_email("sch")

        try:
            httpx.post(
                f"{NGINX_URL}{API_BASE}/internal/user-created",
                json={"userId": tutor_id, "email": email, "realmRole": "tutor"},
                timeout=10,
            )

            # Создание регулярных слотов (пн, ср, пт)
            slots = []
            for day in [1, 3, 5]:
                resp = httpx.post(
                    f"{NGINX_URL}{API_BASE}/schedules",
                    json={
                        "tutor_id": tutor_id,
                        "day_of_week": day,
                        "start_time": "09:00",
                        "end_time": "12:00",
                    },
                    timeout=10,
                )
                assert resp.status_code == 201
                slots.append(resp.json())

            assert len(slots) == 3

            # Получение расписания
            resp = httpx.get(
                f"{NGINX_URL}{API_BASE}/schedules",
                params={"tutor_id": tutor_id},
                timeout=10,
            )
            assert resp.status_code == 200
            assert len(resp.json()) == 3

            # Чтение одного слота по ID
            resp = httpx.get(
                f"{NGINX_URL}{API_BASE}/schedules/{slots[0]['id']}", timeout=10
            )
            assert resp.status_code == 200
            assert resp.json()["day_of_week"] == 1
            assert resp.json()["start_time"] == "09:00:00"

            # Обновление слота
            resp = httpx.patch(
                f"{NGINX_URL}{API_BASE}/schedules/{slots[0]['id']}",
                json={"start_time": "10:00", "end_time": "14:00"},
                timeout=10,
            )
            assert resp.status_code == 200
            assert resp.json()["start_time"] == "10:00:00"

            # Удаление одного слота
            resp = httpx.delete(
                f"{NGINX_URL}{API_BASE}/schedules/{slots[0]['id']}", timeout=10
            )
            assert resp.status_code == 204

            # Осталось 2
            resp = httpx.get(
                f"{NGINX_URL}{API_BASE}/schedules",
                params={"tutor_id": tutor_id},
                timeout=10,
            )
            assert len(resp.json()) == 2

            # Удаляем остальные
            for slot in slots[1:]:
                httpx.delete(
                    f"{NGINX_URL}{API_BASE}/schedules/{slot['id']}", timeout=10
                )

        finally:
            httpx.delete(f"{NGINX_URL}{API_BASE}/users/{tutor_id}", timeout=5)

    def test_tutor_certifications(self):
        """Сертификаты репетитора: создание и просмотр."""
        tutor_id = str(uuid.uuid4())
        email = _random_email("cert")

        try:
            httpx.post(
                f"{NGINX_URL}{API_BASE}/internal/user-created",
                json={"userId": tutor_id, "email": email, "realmRole": "tutor"},
                timeout=10,
            )

            # Добавление сертификата
            resp = httpx.post(
                f"{NGINX_URL}{API_BASE}/tutor_certifications",
                json={
                    "tutor_id": tutor_id,
                    "title": "Сертификат IELTS",
                    "file_url": "https://example.com/ielts.pdf",
                },
                timeout=10,
            )
            assert resp.status_code == 201
            _cert_id = resp.json()["id"]

            # Список сертификатов
            resp = httpx.get(
                f"{NGINX_URL}{API_BASE}/tutor_certifications",
                params={"tutor_id": tutor_id},
                timeout=10,
            )
            assert resp.status_code == 200
            assert len(resp.json()) == 1
            assert resp.json()[0]["title"] == "Сертификат IELTS"

        finally:
            httpx.delete(f"{NGINX_URL}{API_BASE}/users/{tutor_id}", timeout=5)

    def test_schedule_specific_date(self):
        """Создание разового слота расписания (specific_date)."""
        tutor_id = str(uuid.uuid4())
        email = _random_email("spec")

        try:
            httpx.post(
                f"{NGINX_URL}{API_BASE}/internal/user-created",
                json={"userId": tutor_id, "email": email, "realmRole": "tutor"},
                timeout=10,
            )

            future_date = (datetime.now(timezone.utc) + timedelta(days=14)).strftime(
                "%Y-%m-%d"
            )
            resp = httpx.post(
                f"{NGINX_URL}{API_BASE}/schedules",
                json={
                    "tutor_id": tutor_id,
                    "specific_date": future_date,
                    "start_time": "14:00",
                    "end_time": "16:00",
                },
                timeout=10,
            )
            assert resp.status_code == 201
            assert resp.json()["specific_date"] == future_date

        finally:
            httpx.delete(f"{NGINX_URL}{API_BASE}/users/{tutor_id}", timeout=5)
