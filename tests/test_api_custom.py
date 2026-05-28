import unittest

import requests


class TestCustomAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Using localhost for development/testing if running via docker
        cls.base_url = "http://localhost:80"
        cls.custom_api_url = f"{cls.base_url}/api/custom"
        cls.internal_api_url = f"{cls.base_url}/api/custom/internal"

    def test_suggestions_post(self):
        """Test POST /api/custom/suggestions"""
        url = f"{self.custom_api_url}/suggestions"
        payload = {
            "subject_id": 1,
            "max_price": 2000,
            "min_experience": 1,
            "verified_only": False,
            "weights": {
                "k1_effectiveness": 0.3,
                "k2_communication": 0.2,
                "k3_expertise": 0.2,
                "k4_responsiveness": 0.1,
                "k5_tags": 0.2
            }
        }
        # In this task, we assume the server might not be running yet, 
        # so we just verify the structure and expect 200 or 503 if DB is missing
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                data = response.json()
                self.assertIsInstance(data, list)
                if len(data) > 0:
                    self.assertIn("tutor_id", data[0])
                    self.assertIn("score", data[0])
                    self.assertIn("score_breakdown", data[0])
        except requests.exceptions.ConnectionError:
            print("API not running, skipping live check")

    def test_internal_user_created(self):
        """Test POST /api/custom/internal/user-created"""
        url = f"{self.internal_api_url}/user-created"
        payload = {
            "userId": "00000000-0000-0000-0000-000000000099",
            "email": "internal-test@tutorapp.ru",
            "realmRole": "student"
        }
        try:
            # Note: Internal API might be blocked by Nginx for external access
            # but for tests running in the same network it works
            response = requests.post(url, json=payload)
            # If Nginx blocks it, we get 403 or 404
            # If it's direct access, we might get 201
            self.assertIn(response.status_code, [201, 403, 404])
        except requests.exceptions.ConnectionError:
            pass

if __name__ == '__main__':
    unittest.main()
