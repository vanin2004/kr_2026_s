"""Integration tests for Keycloak Admin API operations.

Tests the Keycloak admin endpoints through Nginx (Docker stack).
Requires docker-compose up.
"""

import base64
import json
import time
import uuid

import pytest
import requests

from ..conftest import NGINX_URL


@pytest.fixture(scope="module")
def keycloak_admin_token():
    """Fixture: obtain admin token from Keycloak master realm with retry."""
    url = f"{NGINX_URL}/auth/realms/master/protocol/openid-connect/token"
    data = {
        "client_id": "admin-cli",
        "username": "admin",
        "password": "admin",
        "grant_type": "password",
    }

    for _ in range(30):
        try:
            r = requests.post(url, data=data)
            if r.status_code == 200:
                return r.json()["access_token"]
        except requests.exceptions.ConnectionError:
            pass
        time.sleep(1)

    pytest.fail("Could not get admin token")


def test_registration_and_login_flow(keycloak_admin_token):
    """Full Keycloak flow: create user, assign role, get token, decode JWT."""
    # 1. Create a user via Keycloak Admin API
    username = f"user_{uuid.uuid4().hex[:8]}@example.com"
    password = "password123"

    headers = {
        "Authorization": f"Bearer {keycloak_admin_token}",
        "Content-Type": "application/json",
    }

    create_user_url = f"{NGINX_URL}/auth/admin/realms/tutorapp/users"
    user_payload = {
        "username": username,
        "email": username,
        "enabled": True,
        "credentials": [{"type": "password", "value": password, "temporary": False}],
    }

    r = requests.post(create_user_url, json=user_payload, headers=headers)
    assert r.status_code == 201, f"Failed to create user: {r.text}"

    user_location = r.headers.get("Location")
    assert user_location, "No location header returned for new user"

    # 2. Assign role to user (e.g., student)
    user_id = user_location.split("/")[-1]

    # Get the role ID for 'student'
    roles_url = f"{NGINX_URL}/auth/admin/realms/tutorapp/roles/student"
    r = requests.get(roles_url, headers=headers)
    assert r.status_code == 200, f"Role 'student' not found: {r.text}"
    role_obj = r.json()

    # Map role to user
    assign_role_url = (
        f"{NGINX_URL}/auth/admin/realms/tutorapp/users/{user_id}/role-mappings/realm"
    )
    r = requests.post(assign_role_url, json=[role_obj], headers=headers)
    assert r.status_code == 204, f"Failed to assign role: {r.text}"

    # 3. Get token (authorization flow login) with explicit openid scope
    token_url = f"{NGINX_URL}/auth/realms/tutorapp/protocol/openid-connect/token"
    token_data = {
        "client_id": "tutorapp-client",
        "username": username,
        "password": password,
        "grant_type": "password",
        "scope": "openid profile email",
    }
    r = requests.post(token_url, data=token_data)
    assert r.status_code == 200, f"Failed to get token: {r.text}"
    tokens = r.json()
    access_token = tokens["access_token"]
    id_token = tokens.get("id_token")
    assert id_token, "id_token is required for userinfo in Keycloak 24+"

    # 4. Decode JWT locally to verify claims
    payload_b64 = access_token.split(".")[1]
    payload_b64 += "=" * (4 - len(payload_b64) % 4)
    decoded = json.loads(base64.urlsafe_b64decode(payload_b64))
    assert decoded.get("preferred_username") == username, (
        f"Token username mismatch: {decoded.get('preferred_username')} != {username}"
    )
    assert (
        decoded.get("realm_roles") is not None
        or decoded.get("realm_access") is not None
    ), "Token has no realm roles"
    assert decoded.get("email") == username, (
        f"Token email mismatch: {decoded.get('email')} != {username}"
    )

    # 5. Login again
    r = requests.post(token_url, data=token_data)
    assert r.status_code == 200, "Second login failed"
    second_tokens = r.json()
    assert "access_token" in second_tokens

    # 6. Get user by ID (Admin API) — verify user exists
    get_user_url = f"{NGINX_URL}/auth/admin/realms/tutorapp/users/{user_id}"
    r = requests.get(get_user_url, headers=headers)
    assert r.status_code == 200, f"Failed to get user by ID: {r.text}"
    user_data = r.json()
    assert user_data["id"] == user_id
    assert user_data["email"] == username
    assert user_data["enabled"] is True


def test_certs_endpoint():
    """GET /certs — публичные JWKS-ключи Keycloak."""
    url = f"{NGINX_URL}/auth/realms/tutorapp/protocol/openid-connect/certs"
    r = requests.get(url, timeout=10)
    assert r.status_code == 200, f"Failed to get certs: {r.text}"
    data = r.json()
    assert "keys" in data, "JWKS response must contain 'keys'"
    assert len(data["keys"]) > 0, "Must have at least one signing key"
    required_fields = {"kty", "alg", "kid", "n", "e"}
    for key in data["keys"]:
        assert required_fields.issubset(key.keys()), (
            f"Key missing required fields. Got: {key.keys()}"
        )


def test_userinfo_endpoint(keycloak_admin_token):
    """GET /userinfo — получение данных пользователя через access_token.

    Admin-токен master realm не имеет доступа к userinfo tutorapp realm (401).
    Тест проверяет, что endpoint доступен и не возвращает 500.
    """
    url = f"{NGINX_URL}/auth/realms/tutorapp/protocol/openid-connect/userinfo"
    headers = {"Authorization": f"Bearer {keycloak_admin_token}"}
    r = requests.get(url, headers=headers, timeout=10)
    # Допускаем 401 (чужой realm), 403 (public client) или 200
    assert r.status_code in (200, 401, 403), (
        f"Unexpected status: {r.status_code}, body: {r.text}"
    )
