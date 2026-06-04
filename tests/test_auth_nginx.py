import base64
import json
import time
import uuid

import pytest
import requests
from .conftest import NGINX_URL


@pytest.fixture(scope="module")
def keycloak_admin_token():
    # Wait for keycloak to be ready? We assume it is running.
    url = f"{NGINX_URL}/auth/realms/master/protocol/openid-connect/token"
    data = {
        "client_id": "admin-cli",
        "username": "admin",
        "password": "admin",
        "grant_type": "password",
    }

    # Simple retry mechanism if Keycloak is starting
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
    # 1. Create a user via Keycloak Admin API (wrapped nicely)
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

    # 4. Decode JWT locally to verify claims (userinfo/introspection
    #    may return 403 for public clients)
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
