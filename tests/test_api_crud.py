import unittest
import uuid

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class TestAPICRUD(unittest.TestCase):
    BASE_URL = "http://157.245.244.194:80/api/data"

    @classmethod
    def setUpClass(cls):
        # Настройка сессии с ретраями для стабильности на нестабильных соединениях
        cls.session = requests.Session()
        retries = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[500, 502, 503, 504]
        )
        cls.session.mount("http://", HTTPAdapter(max_retries=retries))

    def setUp(self):
        self.test_user_id = str(uuid.uuid4())
        self.student_id = str(uuid.uuid4())
        self.tutor_id = str(uuid.uuid4())
        self.created_subjects = []
        self.created_tags = []

    def tearDown(self):
        # Очистка созданных пользователей
        for uid in [self.test_user_id, self.student_id, self.tutor_id]:
            try:
                self.session.delete(f"{self.BASE_URL}/users?id=eq.{uid}", timeout=10)
            except Exception:
                pass
        
        # Очистка созданных предметов
        for name in self.created_subjects:
            try:
                self.session.delete(f"{self.BASE_URL}/subjects?name=eq.{name}", timeout=10)
            except Exception:
                pass

        # Очистка созданных тегов
        for name in self.created_tags:
            try:
                self.session.delete(f"{self.BASE_URL}/tags?name=eq.{name}", timeout=10)
            except Exception:
                pass

    def test_01_health_check_via_subjects(self):
        """Проверка доступности API через таблицу subjects."""
        response = self.session.get(f"{self.BASE_URL}/subjects", timeout=15)
        self.assertEqual(response.status_code, 200)

    def test_02_full_user_and_profile_flow(self):
        """Тестирование создания пользователя и профиля."""
        # 1. Создаем пользователя
        user_data = {
            "id": self.test_user_id,
            "email": f"test_{self.test_user_id}@example.com",
            "role": "tutor"
        }
        resp = self.session.post(f"{self.BASE_URL}/users", json=user_data, timeout=15)
        self.assertEqual(resp.status_code, 201)

        # 2. Создаем профиль репетитора
        profile_data = {
            "user_id": self.test_user_id,
            "full_name": "Test Tutor",
            "hourly_rate": 150000
        }
        resp = self.session.post(f"{self.BASE_URL}/tutor_profiles", json=profile_data, timeout=15)
        self.assertEqual(resp.status_code, 201)

        # 3. Обновляем профиль (PATCH)
        update_data = {"full_name": "Updated Tutor Name"}
        resp = self.session.patch(f"{self.BASE_URL}/tutor_profiles?user_id=eq.{self.test_user_id}", json=update_data, timeout=15)
        self.assertEqual(resp.status_code, 204)

        # 4. Проверяем результат (GET)
        resp = self.session.get(f"{self.BASE_URL}/tutor_profiles?user_id=eq.{self.test_user_id}", timeout=15)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()[0]["full_name"], "Updated Tutor Name")

    def test_03_application_flow(self):
        """Тестирование создания и обновления заявки."""
        # Подготовка субъектов
        subject_name = f"Subject_{uuid.uuid4().hex[:6]}"
        resp = self.session.post(f"{self.BASE_URL}/subjects", json={"name": subject_name}, timeout=15)
        self.assertEqual(resp.status_code, 201)
        self.created_subjects.append(subject_name)

        resp = self.session.get(f"{self.BASE_URL}/subjects?name=eq.{subject_name}", timeout=15)
        self.assertEqual(resp.status_code, 200)
        subj_id = resp.json()[0]["id"]

        # Создаем участников
        self.session.post(f"{self.BASE_URL}/users", json={"id": self.student_id, "email": f"s_{self.student_id}@ex.com", "role": "student"}, timeout=15)
        self.session.post(f"{self.BASE_URL}/users", json={"id": self.tutor_id, "email": f"t_{self.tutor_id}@ex.com", "role": "tutor"}, timeout=15)
        self.session.post(f"{self.BASE_URL}/tutor_profiles", json={"user_id": self.tutor_id, "subject_id": subj_id}, timeout=15)

        # 1. Создание заявки
        app_id = str(uuid.uuid4())
        app_data = {
            "id": app_id,
            "student_id": self.student_id,
            "tutor_id": self.tutor_id,
            "status": "pending"
        }
        resp = self.session.post(f"{self.BASE_URL}/applications", json=app_data, timeout=15)
        self.assertEqual(resp.status_code, 201)

        # 2. Принятие заявки
        resp = self.session.patch(f"{self.BASE_URL}/applications?id=eq.{app_id}", json={"status": "accepted"}, timeout=15)
        self.assertEqual(resp.status_code, 204)

    def test_04_tags_operations(self):
        """Тестирование справочника тегов."""
        tag_name = f"tag_{uuid.uuid4().hex[:8]}"
        
        # Create
        resp = self.session.post(f"{self.BASE_URL}/tags", json={"name": tag_name}, timeout=15)
        self.assertEqual(resp.status_code, 201)
        self.created_tags.append(tag_name)

        resp = self.session.get(f"{self.BASE_URL}/tags?name=eq.{tag_name}", timeout=15)
        self.assertEqual(resp.status_code, 200)
        tag_id = resp.json()[0]["id"]

        # Delete
        resp = self.session.delete(f"{self.BASE_URL}/tags?id=eq.{tag_id}", timeout=15)
        self.assertEqual(resp.status_code, 204)

if __name__ == "__main__":
    unittest.main()
