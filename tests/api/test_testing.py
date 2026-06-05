"""
Интеграционные тесты — тестирование (назначение, прохождение, результаты).

Приложение запущено в Docker. Тесты ходят по HTTP через Nginx.
"""

import uuid
from datetime import datetime, timezone

import httpx

from ..conftest import API_BASE, NGINX_URL


def _random_email(prefix: str = "test") -> str:
    """Уникальный email для тестов."""
    return f"{prefix}-{uuid.uuid4().hex[:8]}@test.local"


class TestTesting:
    """Назначение теста, прохождение, просмотр результатов."""

    def test_student_results_lifecycle(self):
        """Жизненный цикл результата теста."""
        tutor_id = str(uuid.uuid4())
        student_id = str(uuid.uuid4())
        subject_id = None

        try:
            # Создаём предмет
            resp = httpx.post(
                f"{NGINX_URL}{API_BASE}/subjects",
                json={"name": f"Тест-предмет-{uuid.uuid4().hex[:4]}"},
                timeout=10,
            )
            subject_id = resp.json()["id"]

            # Создаём пользователей
            for uid, role, name in [
                (tutor_id, "tutor", "t-test"),
                (student_id, "student", "s-test"),
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

            # Создаём тест в библиотеке
            resp = httpx.post(
                f"{NGINX_URL}{API_BASE}/test_library",
                json={
                    "subject_id": subject_id,
                    "topic": "Интеграционный тест",
                    "questions_json": {
                        "questions": [
                            {"q": "1+1?", "answers": ["1", "2", "3"], "correct": 1}
                        ]
                    },
                },
                timeout=10,
            )
            assert resp.status_code == 201
            test_id = resp.json()["id"]

            # Назначение теста
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
            assert resp.json()["score"] is None

            # Прохождение теста (заполнение score и completed_at)
            resp = httpx.patch(
                f"{NGINX_URL}{API_BASE}/student_results/{result_id}",
                json={
                    "score": "92.00",
                    "completed_at": datetime.now(timezone.utc).isoformat(),
                },
                timeout=10,
            )
            assert resp.status_code == 200
            assert float(resp.json()["score"]) == 92.00
            assert resp.json()["completed_at"] is not None

            # Проверка списка результатов
            resp = httpx.get(
                f"{NGINX_URL}{API_BASE}/student_results",
                params={"student_id": student_id},
                timeout=10,
            )
            assert resp.status_code == 200
            assert any(r["id"] == result_id for r in resp.json())

            # Фильтрация результатов по репетитору
            resp = httpx.get(
                f"{NGINX_URL}{API_BASE}/student_results",
                params={"tutor_id": tutor_id},
                timeout=10,
            )
            assert resp.status_code == 200
            assert len(resp.json()) >= 1

        finally:
            for uid in [tutor_id, student_id]:
                httpx.delete(f"{NGINX_URL}{API_BASE}/users/{uid}", timeout=5)
            if subject_id:
                httpx.delete(f"{NGINX_URL}{API_BASE}/subjects/{subject_id}", timeout=5)
