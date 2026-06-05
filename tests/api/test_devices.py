"""
Интеграционные тесты — управление FCM-токенами устройств.

Приложение запущено в Docker. Тесты ходят по HTTP через Nginx.
"""

import uuid

import httpx

from ..conftest import API_BASE, NGINX_URL


def _random_email(prefix: str = "test") -> str:
    """Уникальный email для тестов."""
    return f"{prefix}-{uuid.uuid4().hex[:8]}@test.local"


class TestDeviceTokens:
    """Управление FCM-токенами устройств."""

    def test_device_token_lifecycle(self):
        """Создание, просмотр, удаление device token."""
        user_id = str(uuid.uuid4())

        try:
            httpx.post(
                f"{NGINX_URL}{API_BASE}/internal/user-created",
                json={
                    "userId": user_id,
                    "email": _random_email("dt"),
                    "realmRole": "student",
                },
                timeout=10,
            )

            # Создание
            token_value = f"fcm-int-{uuid.uuid4().hex}"
            resp = httpx.post(
                f"{NGINX_URL}{API_BASE}/device_tokens",
                json={
                    "user_id": user_id,
                    "token": token_value,
                    "platform": "android",
                },
                timeout=10,
            )
            assert resp.status_code == 201
            token_id = resp.json()["id"]
            assert resp.json()["platform"] == "android"

            # Просмотр
            resp = httpx.get(
                f"{NGINX_URL}{API_BASE}/device_tokens",
                params={"user_id": user_id},
                timeout=10,
            )
            assert resp.status_code == 200
            assert any(t["id"] == token_id for t in resp.json())

            # Удаление
            resp = httpx.delete(
                f"{NGINX_URL}{API_BASE}/device_tokens/{token_id}", timeout=10
            )
            assert resp.status_code == 204

            # Проверка удаления
            resp = httpx.get(
                f"{NGINX_URL}{API_BASE}/device_tokens",
                params={"user_id": user_id},
                timeout=10,
            )
            assert all(t["id"] != token_id for t in resp.json())

        finally:
            httpx.delete(f"{NGINX_URL}{API_BASE}/users/{user_id}", timeout=5)
