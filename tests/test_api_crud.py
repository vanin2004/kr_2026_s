import unittest
import uuid

import requests


class TestAPICRUD(unittest.TestCase):
    BASE_URL = "http://localhost/api/data"

    def setUp(self):
        self.test_user_id = str(uuid.uuid4())
        self.student_id = str(uuid.uuid4())
        self.tutor_id = str(uuid.uuid4())

    def tearDown(self):
        # Очистка созданных пользователей
        for uid in [self.test_user_id, self.student_id, self.tutor_id]:
            requests.delete(f"{self.BASE_URL}/users?id=eq.{uid}")

    def test_01_health_check_via_subjects(self):
        """Проверка доступности API через таблицу subjects."""
        response = requests.get(f"{self.BASE_URL}/subjects")
        self.assertEqual(response.status_code, 200)

    def test_02_full_user_and_profile_flow(self):
        """Тестирование создания пользователя и профиля."""
        # 1. Создаем пользователя
        user_data = {
            "id": self.test_user_id,
            "email": f"test_{self.test_user_id}@example.com",
            "role": "tutor"
        }
        resp = requests.post(f"{self.BASE_URL}/users", json=user_data)
        self.assertEqual(resp.status_code, 201)

        # 2. Создаем профиль репетитора
        profile_data = {
            "user_id": self.test_user_id,
            "full_name": "Test Tutor",
            "hourly_rate": 150000
        }
        resp = requests.post(f"{self.BASE_URL}/tutor_profiles", json=profile_data)
        self.assertEqual(resp.status_code, 201)

        # 3. Обновляем профиль (PATCH)
        update_data = {"full_name": "Updated Tutor Name"}
        resp = requests.patch(f"{self.BASE_URL}/tutor_profiles?user_id=eq.{self.test_user_id}", json=update_data)
        self.assertEqual(resp.status_code, 204)

        # 4. Проверяем результат (GET)
        resp = requests.get(f"{self.BASE_URL}/tutor_profiles?user_id=eq.{self.test_user_id}")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()[0]["full_name"], "Updated Tutor Name")

    def test_03_application_flow(self):
        """Тестирование создания и обновления заявки."""
        # Подготовка субъектов (используем уникальное имя, чтобы не было конфликтов)
        subject_name = f"Subject_{uuid.uuid4().hex[:6]}"
        requests.post(f"{self.BASE_URL}/subjects", json={"name": subject_name})
        subj_id = requests.get(f"{self.BASE_URL}/subjects?name=eq.{subject_name}").json()[0]["id"]

        # Создаем участников
        requests.post(f"{self.BASE_URL}/users", json={"id": self.student_id, "email": f"s_{self.student_id}@ex.com", "role": "student"})
        requests.post(f"{self.BASE_URL}/users", json={"id": self.tutor_id, "email": f"t_{self.tutor_id}@ex.com", "role": "tutor"})
        requests.post(f"{self.BASE_URL}/tutor_profiles", json={"user_id": self.tutor_id, "subject_id": subj_id})

        # 1. Создание заявки
        app_id = str(uuid.uuid4())
        app_data = {
            "id": app_id,
            "student_id": self.student_id,
            "tutor_id": self.tutor_id,
            "status": "pending"
        }
        resp = requests.post(f"{self.BASE_URL}/applications", json=app_data)
        self.assertEqual(resp.status_code, 201)

        # 2. Принятие заявки
        resp = requests.patch(f"{self.BASE_URL}/applications?id=eq.{app_id}", json={"status": "accepted"})
        self.assertEqual(resp.status_code, 204)

    def test_04_tags_operations(self):
        """Тестирование справочника тегов."""
        tag_name = f"tag_{uuid.uuid4().hex[:8]}"
        
        # Create
        resp = requests.post(f"{self.BASE_URL}/tags", json={"name": tag_name})
        self.assertEqual(resp.status_code, 201)
        tag_id = requests.get(f"{self.BASE_URL}/tags?name=eq.{tag_name}").json()[0]["id"]

        # Delete
        resp = requests.delete(f"{self.BASE_URL}/tags?id=eq.{tag_id}")
        self.assertEqual(resp.status_code, 204)

if __name__ == "__main__":
    unittest.main()
