"""Integration tests for the auth registration endpoint.

Hits the real running API through Nginx (Docker stack).
Requires docker-compose up.
"""

import uuid

import pytest
import requests

from ..conftest import API_BASE, NGINX_URL

REGISTER_URL = f"{NGINX_URL}{API_BASE}/auth/register"
KC_ADMIN_URL = f"{NGINX_URL}/auth/admin/realms/tutorapp"


def _kc_admin_token() -> str:
    """Get admin token from Keycloak master realm."""
    url = f"{NGINX_URL}/auth/realms/master/protocol/openid-connect/token"
    data = {
        "client_id": "admin-cli",
        "username": "admin",
        "password": "admin",
        "grant_type": "password",
    }
    r = requests.post(url, data=data, timeout=10)
    r.raise_for_status()
    return r.json()["access_token"]


def _kc_delete_user(username: str, token: str) -> None:
    """Delete a Keycloak user by username."""
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(
        f"{KC_ADMIN_URL}/users",
        params={"username": username},
        headers=headers,
        timeout=10,
    )
    if r.status_code == 200 and r.json():
        user_id = r.json()[0]["id"]
        requests.delete(
            f"{KC_ADMIN_URL}/users/{user_id}",
            headers=headers,
            timeout=10,
        )


class TestRegisterIntegration:
    """POST /api/custom/auth/register — integration tests."""

    REGISTER_URL = REGISTER_URL

    @pytest.fixture(autouse=True)
    def cleanup(self):
        """Generate a unique username so parallel runs don't collide."""
        self.username = f"testuser_{uuid.uuid4().hex[:8]}"
        self.password = "secret123"
        yield
        # Cleanup Keycloak
        try:
            token = _kc_admin_token()
            _kc_delete_user(self.username, token)
        except Exception:
            pass

    def test_register_student(self):
        """Register a student, then verify they can login via Keycloak."""
        payload = {
            "username": self.username,
            "password": self.password,
            "full_name": "Тестовый Студент",
            "role": "student",
        }
        r = requests.post(self.REGISTER_URL, json=payload, timeout=15)
        assert r.status_code == 201, f"Registration failed: {r.text}"
        data = r.json()
        assert data["username"] == self.username
        assert data["role"] == "student"
        assert uuid.UUID(data["user_id"])

        # Verify user exists in the local DB (via users endpoint)
        r = requests.get(
            f"{NGINX_URL}{API_BASE}/users",
            timeout=10,
        )
        assert r.status_code == 200
        all_users = r.json()
        user_ids = [u["id"] for u in all_users]
        assert data["user_id"] in user_ids, "User not found in local DB"

        # Try logging in via Keycloak Direct Access Grants
        token_url = f"{NGINX_URL}/auth/realms/tutorapp/protocol/openid-connect/token"
        login_data = {
            "client_id": "tutorapp-client",
            "username": self.username,
            "password": self.password,
            "grant_type": "password",
            "scope": "openid profile email",
        }
        r = requests.post(token_url, data=login_data, timeout=10)
        assert r.status_code == 200, f"Login failed: {r.text}"
        tokens = r.json()
        assert "access_token" in tokens

    def test_register_tutor(self):
        """Register a tutor with subject and rate."""
        # Get a subject ID first
        r = requests.get(f"{NGINX_URL}{API_BASE}/subjects", timeout=10)
        assert r.status_code == 200
        subjects = r.json()
        assert len(subjects) > 0, "No subjects available"
        subject_id = subjects[0]["id"]

        payload = {
            "username": self.username,
            "password": self.password,
            "full_name": "Тестовый Репетитор",
            "role": "tutor",
            "subject_id": subject_id,
            "hourly_rate": 2000,
        }
        r = requests.post(self.REGISTER_URL, json=payload, timeout=15)
        assert r.status_code == 201, f"Registration failed: {r.text}"
        data = r.json()
        assert data["role"] == "tutor"

        # Verify tutor profile — endpoint uses underscore, not dash
        r = requests.get(f"{NGINX_URL}{API_BASE}/tutor_profiles", timeout=10)
        assert r.status_code == 200
        profiles = r.json()
        tutor_ids = [p["user_id"] for p in profiles]
        assert data["user_id"] in tutor_ids, "Tutor profile not found"

    def test_register_duplicate_username(self):
        """Register the same username twice should fail with 409."""
        payload = {
            "username": self.username,
            "password": self.password,
            "full_name": "First",
            "role": "student",
        }
        r = requests.post(self.REGISTER_URL, json=payload, timeout=15)
        assert r.status_code == 201, f"First registration failed: {r.text}"

        # Second attempt
        r = requests.post(self.REGISTER_URL, json=payload, timeout=15)
        assert r.status_code == 409, f"Expected 409, got {r.status_code}: {r.text}"

    def test_register_missing_fields(self):
        """Missing required fields should return 422."""
        payload = {
            "username": self.username,
            # missing password, full_name, role
        }
        r = requests.post(self.REGISTER_URL, json=payload, timeout=15)
        assert r.status_code == 422, f"Expected 422, got {r.status_code}"

    def test_register_tutor_missing_subject(self):
        """Tutor without subject_id should return 422."""
        payload = {
            "username": self.username,
            "password": self.password,
            "full_name": "Tutor No Subject",
            "role": "tutor",
        }
        r = requests.post(self.REGISTER_URL, json=payload, timeout=15)
        assert r.status_code == 422

    def test_register_tutor_missing_rate(self):
        """Tutor without hourly_rate should return 422."""
        payload = {
            "username": self.username,
            "password": self.password,
            "full_name": "Tutor No Rate",
            "role": "tutor",
            "subject_id": "10000001-0000-0000-0000-000000000001",
        }
        r = requests.post(self.REGISTER_URL, json=payload, timeout=15)
        assert r.status_code == 422

    def test_register_invalid_role(self):
        """Invalid role should return 422."""
        payload = {
            "username": self.username,
            "password": self.password,
            "full_name": "Invalid",
            "role": "admin",
        }
        r = requests.post(self.REGISTER_URL, json=payload, timeout=15)
        assert r.status_code == 422
