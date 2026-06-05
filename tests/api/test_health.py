"""
Интеграционные тесты — базовая проверка доступности сервиса.

Приложение запущено в Docker. Тесты ходят по HTTP через Nginx.
"""

import httpx

from ..conftest import NGINX_URL


class TestAPI:
    """Проверка, что сервис жив."""

    def test_health_check(self):
        """GET /health — проверка, что сервис жив."""
        response = httpx.get(f"{NGINX_URL}/health", timeout=10)
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
