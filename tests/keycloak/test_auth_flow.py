"""Integration tests for Keycloak authentication flow — logout.

Tests the logout flow through Nginx (Docker stack).
Requires docker-compose up.
"""

import uuid

import requests

from ..conftest import NGINX_URL


def test_logout_flow():
    """POST /logout — инвалидация refresh token."""
    # Создаём временного пользователя для logout
    username = f"logout_{uuid.uuid4().hex[:8]}@example.com"
    password = "password123"

    # Получаем admin токен
    admin_url = f"{NGINX_URL}/auth/realms/master/protocol/openid-connect/token"
    admin_data = {
        "client_id": "admin-cli",
        "username": "admin",
        "password": "admin",
        "grant_type": "password",
    }
    r = requests.post(admin_url, data=admin_data, timeout=10)
    assert r.status_code == 200, "Failed to get admin token"
    admin_token = r.json()["access_token"]

    headers = {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json",
    }

    # Создаём пользователя
    create_url = f"{NGINX_URL}/auth/admin/realms/tutorapp/users"
    user_payload = {
        "username": username,
        "email": username,
        "enabled": True,
        "credentials": [{"type": "password", "value": password, "temporary": False}],
    }
    r = requests.post(create_url, json=user_payload, headers=headers, timeout=10)
    assert r.status_code == 201, f"Failed to create user for logout: {r.text}"

    user_id = r.headers.get("Location", "").split("/")[-1]

    # Назначаем роль
    roles_url = f"{NGINX_URL}/auth/admin/realms/tutorapp/roles/student"
    r = requests.get(roles_url, headers=headers, timeout=10)
    assert r.status_code == 200
    role_obj = r.json()

    assign_url = (
        f"{NGINX_URL}/auth/admin/realms/tutorapp/users/{user_id}/role-mappings/realm"
    )
    r = requests.post(assign_url, json=[role_obj], headers=headers, timeout=10)
    assert r.status_code == 204

    # Получаем токен (нужен refresh_token для logout)
    token_url = f"{NGINX_URL}/auth/realms/tutorapp/protocol/openid-connect/token"
    token_data = {
        "client_id": "tutorapp-client",
        "username": username,
        "password": password,
        "grant_type": "password",
        "scope": "openid profile email",
    }
    r = requests.post(token_url, data=token_data, timeout=10)
    assert r.status_code == 200, f"Failed to get token for logout: {r.text}"
    tokens = r.json()
    refresh_token = tokens["refresh_token"]
    assert refresh_token, "Must have refresh_token"

    # Выполняем logout
    logout_url = f"{NGINX_URL}/auth/realms/tutorapp/protocol/openid-connect/logout"
    logout_data = {
        "client_id": "tutorapp-client",
        "refresh_token": refresh_token,
    }
    r = requests.post(logout_url, data=logout_data, timeout=10)
    assert r.status_code == 204, f"Logout failed: {r.status_code} {r.text}"

    # Пытаемся использовать старый refresh token — он должен быть невалидным
    r = requests.post(token_url, data=token_data, timeout=10)
    assert r.status_code == 200, "Should still login fresh (different session)"

    # Пробуем обновить токен по старому refresh_token — должен упасть
    refresh_data = {
        "client_id": "tutorapp-client",
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    }
    r = requests.post(token_url, data=refresh_data, timeout=10)
    assert r.status_code == 400, (
        f"Old refresh token should be invalid: {r.status_code} {r.text}"
    )
