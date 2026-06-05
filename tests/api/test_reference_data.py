"""
Интеграционные тесты — справочники (Subjects и Tags).

Приложение запущено в Docker. Тесты ходят по HTTP через Nginx.
"""

import httpx

from ..conftest import API_BASE, NGINX_URL


class TestReferenceData:
    """CRUD для справочников: subjects и tags."""

    def test_subjects_crud(self):
        """Полный CRUD для предметов."""
        # Create
        resp = httpx.post(
            f"{NGINX_URL}{API_BASE}/subjects",
            json={"name": "Интеграционный тест"},
            timeout=10,
        )
        assert resp.status_code == 201
        assert resp.json()["name"] == "Интеграционный тест"
        subject_id = resp.json()["id"]

        try:
            # Read
            resp = httpx.get(f"{NGINX_URL}{API_BASE}/subjects/{subject_id}", timeout=10)
            assert resp.status_code == 200
            assert resp.json()["name"] == "Интеграционный тест"

            # Update
            resp = httpx.patch(
                f"{NGINX_URL}{API_BASE}/subjects/{subject_id}",
                json={"name": "Интеграционный тест (изменён)"},
                timeout=10,
            )
            assert resp.status_code == 200
            assert resp.json()["name"] == "Интеграционный тест (изменён)"

        finally:
            # Delete
            resp = httpx.delete(
                f"{NGINX_URL}{API_BASE}/subjects/{subject_id}", timeout=10
            )
            assert resp.status_code == 204

            # Verify deletion
            resp = httpx.get(f"{NGINX_URL}{API_BASE}/subjects/{subject_id}", timeout=10)
            assert resp.status_code == 404

    def test_tags_crud(self):
        """Полный CRUD для тегов."""
        # Create
        resp = httpx.post(
            f"{NGINX_URL}{API_BASE}/tags",
            json={"name": "интеграционный-тег"},
            timeout=10,
        )
        assert resp.status_code == 201
        tag_id = resp.json()["id"]

        try:
            # Read by ID
            resp = httpx.get(f"{NGINX_URL}{API_BASE}/tags/{tag_id}", timeout=10)
            assert resp.status_code == 200
            assert resp.json()["name"] == "интеграционный-тег"

            # List - тег должен быть в списке
            resp = httpx.get(f"{NGINX_URL}{API_BASE}/tags", timeout=10)
            assert resp.status_code == 200
            assert any(t["id"] == tag_id for t in resp.json())

            # Update
            resp = httpx.patch(
                f"{NGINX_URL}{API_BASE}/tags/{tag_id}",
                json={"name": "тег-обновлён"},
                timeout=10,
            )
            assert resp.status_code == 200

        finally:
            resp = httpx.delete(f"{NGINX_URL}{API_BASE}/tags/{tag_id}", timeout=10)
            assert resp.status_code == 204
