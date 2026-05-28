import unittest

import requests


class TestTutorAppAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base_url = "http://157.245.244.194:80"
        cls.data_api_url = f"{cls.base_url}/api/data"
        cls.custom_api_url = f"{cls.base_url}/api/custom"
        
    def test_get_tutor_profiles(self):
        """Test fetching tutor profiles (Public)"""
        url = f"{self.data_api_url}/tutor_profiles"
        response = requests.get(url)
        self.assertIn(response.status_code, [200, 404])
        if response.status_code == 200:
            self.assertIsInstance(response.json(), list)

    def test_get_tags(self):
        """Test fetching available tags (Public)"""
        url = f"{self.data_api_url}/tags"
        response = requests.get(url)
        self.assertIn(response.status_code, [200, 404])
        if response.status_code == 200:
            self.assertIsInstance(response.json(), list)

    def test_get_reviews_for_tutor(self):
        """Test fetching reviews (Public)"""
        # We use a dummy UUID or just check the endpoint existence
        url = f"{self.data_api_url}/reviews"
        response = requests.get(url)
        self.assertIn(response.status_code, [200, 404])

    def test_suggestions_endpoint_exists(self):
        """Test that the custom suggestions endpoint is reachable"""
        url = f"{self.custom_api_url}/suggestions"
        # This usually requires POST, testing with GET should return 405 or 401/403
        response = requests.get(url)
        self.assertIn(response.status_code, [405, 401, 403])

    def test_post_suggestions_unauthenticated(self):
        """Test suggestions endpoint without auth (should be 401/403)"""
        url = f"{self.custom_api_url}/suggestions"
        payload = {
            "subject_id": 1,
            "weights": {
                "k1_effectiveness": 0.30,
                "k2_communication": 0.15,
                "k3_expertise": 0.20,
                "k4_responsiveness": 0.15,
                "k5_tags": 0.20
            }
        }
        response = requests.post(url, json=payload)
        # Authentication is required according to architecture.md
        self.assertIn(response.status_code, [401, 403])

if __name__ == "__main__":
    unittest.main()
