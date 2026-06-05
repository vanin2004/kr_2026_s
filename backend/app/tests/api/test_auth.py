"""Unit tests for the auth registration endpoint.

Uses in-memory SQLite (via conftest.py fixtures) and mocks `httpx.AsyncClient`
to avoid a real Keycloak dependency.
"""

import uuid
from unittest.mock import AsyncMock

import httpx
import pytest
import pytest_asyncio
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio

# ── Shared mock helpers ──────────────────────────────────────────────


def _mock_response(
    json_data: dict | list | None = None,
    location: str | None = None,
) -> AsyncMock:
    """Build a minimal ``httpx.Response``-like mock."""
    resp = AsyncMock()
    resp.raise_for_status = AsyncMock()
    resp.json = AsyncMock(return_value=json_data or {})
    resp.headers = {}
    if location:
        resp.headers["location"] = location
    return resp


def _patch_kc_client(monkeypatch: pytest.MonkeyPatch) -> AsyncMock:
    """Patch ``httpx.AsyncClient`` with pre-wired responses for the
    ``register`` endpoint.

    Required by ``register`` (in order):
      1. POST …/token              →  ``_kc_admin_token``
      2. GET …/users?username=…    →  ``_kc_user_exists``
      3. POST …/users              →  create user
      4. PUT …/users/…/password    →  set password
      5. GET …/roles               →  ``_kc_role_id``
      6. POST …/users/…/realm      →  assign role
    """
    fake = AsyncMock()

    resp_token = _mock_response({"access_token": "fake-admin-token"})
    resp_empty_list = _mock_response([])
    resp_created = _mock_response(
        location="/admin/realms/tutorapp/users/fake-user-uuid"
    )
    resp_ok = _mock_response()
    resp_roles = _mock_response([{"id": "role-id", "name": "tutor"}])

    # Sequence of POST calls: token, create user, assign role
    fake.post = AsyncMock(side_effect=[resp_token, resp_created, resp_ok])
    # Sequence of GET calls: check user exists, fetch roles
    fake.get = AsyncMock(side_effect=[resp_empty_list, resp_roles])
    # PUT call: set password
    fake.put = AsyncMock(return_value=resp_ok)

    monkeypatch.setattr(
        "api.endpoints.auth.httpx.AsyncClient",
        lambda **kwargs: AsyncMock(
            __aenter__=AsyncMock(return_value=fake),
            __aexit__=AsyncMock(),
        ),
    )
    return fake


# ── Fixtures ──────────────────────────────────────────────────────────


@pytest_asyncio.fixture
async def seed_math_subject(client: AsyncClient) -> dict:
    """Create a math subject via the API (needed for tutor registration)."""
    resp = await client.post(
        "/api/custom/subjects",
        json={"name": "Математика"},
    )
    assert resp.status_code in (200, 201), resp.text
    return resp.json()


# ── Tests ─────────────────────────────────────────────────────────────


class TestRegister:
    """POST /api/custom/auth/register"""

    # -- Success cases --------------------------------------------------

    async def test_register_student_success(
        self, client: AsyncClient, monkeypatch: pytest.MonkeyPatch
    ):
        """Student registration without subject/rate should succeed."""
        _patch_kc_client(monkeypatch)

        payload = {
            "username": "teststudent",
            "password": "secret123",
            "full_name": "Студент Тестович",
            "role": "student",
        }
        resp = await client.post("/api/custom/auth/register", json=payload)
        assert resp.status_code == 201, resp.text
        data = resp.json()
        assert data["username"] == "teststudent"
        assert data["role"] == "student"
        assert uuid.UUID(data["user_id"])

    async def test_register_tutor_success(
        self,
        client: AsyncClient,
        monkeypatch: pytest.MonkeyPatch,
        seed_math_subject: dict,
    ):
        """Tutor registration with subject and rate should succeed."""
        _patch_kc_client(monkeypatch)

        payload = {
            "username": "testtutor",
            "password": "secret123",
            "full_name": "Репетитор Тестович",
            "role": "tutor",
            "subject_id": seed_math_subject["id"],
            "hourly_rate": 1500,
        }
        resp = await client.post("/api/custom/auth/register", json=payload)
        assert resp.status_code == 201, resp.text
        data = resp.json()
        assert data["username"] == "testtutor"
        assert data["role"] == "tutor"
        assert uuid.UUID(data["user_id"])

    # -- Validation errors (Pydantic) ----------------------------------

    async def test_register_tutor_missing_subject(self, client: AsyncClient):
        """Tutor without subject_id should get 422."""
        payload = {
            "username": "bad_tutor",
            "password": "secret123",
            "full_name": "Bad Tutor",
            "role": "tutor",
        }
        resp = await client.post("/api/custom/auth/register", json=payload)
        assert resp.status_code == 422, resp.text

    async def test_register_tutor_missing_rate(self, client: AsyncClient):
        """Tutor without hourly_rate should get 422."""
        payload = {
            "username": "bad_tutor2",
            "password": "secret123",
            "full_name": "Bad Tutor",
            "role": "tutor",
            "subject_id": "10000001-0000-0000-0000-000000000001",
        }
        resp = await client.post("/api/custom/auth/register", json=payload)
        assert resp.status_code == 422, resp.text

    async def test_register_invalid_role(self, client: AsyncClient):
        """Invalid role should get 422."""
        payload = {
            "username": "invalid_role",
            "password": "secret123",
            "full_name": "Test",
            "role": "admin",
        }
        resp = await client.post("/api/custom/auth/register", json=payload)
        assert resp.status_code == 422, resp.text

    # -- Business-logic errors -----------------------------------------

    async def test_register_duplicate_username(
        self, client: AsyncClient, monkeypatch: pytest.MonkeyPatch
    ):
        """Duplicate username in Keycloak should get 409."""
        # mock both helper functions directly — no httpx mocks needed
        monkeypatch.setattr(
            "api.endpoints.auth._kc_admin_token",
            AsyncMock(return_value="fake-token"),
        )
        monkeypatch.setattr(
            "api.endpoints.auth._kc_user_exists",
            AsyncMock(return_value=True),
        )

        payload = {
            "username": "duplicate",
            "password": "secret123",
            "full_name": "Duplicate",
            "role": "student",
        }
        resp = await client.post("/api/custom/auth/register", json=payload)
        assert resp.status_code == 409, resp.text

    async def test_register_keycloak_unavailable(
        self, client: AsyncClient, monkeypatch: pytest.MonkeyPatch
    ):
        """Keycloak connection error should return 502."""
        monkeypatch.setattr(
            "api.endpoints.auth.httpx.AsyncClient",
            lambda **kwargs: AsyncMock(
                __aenter__=AsyncMock(
                    side_effect=httpx.ConnectError("Connection refused")
                ),
                __aexit__=AsyncMock(),
            ),
        )

        payload = {
            "username": "nokc",
            "password": "secret123",
            "full_name": "No KC",
            "role": "student",
        }
        resp = await client.post("/api/custom/auth/register", json=payload)
        assert resp.status_code == 502, resp.text

    async def test_register_invalid_subject_id(
        self, client: AsyncClient, monkeypatch: pytest.MonkeyPatch
    ):
        """Non-existent subject_id should return 400."""
        _patch_kc_client(monkeypatch)

        payload = {
            "username": "badsubject",
            "password": "secret123",
            "full_name": "Bad Subject",
            "role": "tutor",
            "subject_id": "00000000-0000-0000-0000-000000000000",
            "hourly_rate": 1000,
        }
        resp = await client.post("/api/custom/auth/register", json=payload)
        assert resp.status_code == 400, resp.text

    # -- Database side-effects ------------------------------------------

    async def test_register_updates_db(
        self, client: AsyncClient, monkeypatch: pytest.MonkeyPatch
    ):
        """After successful registration, the user should exist in the DB."""
        _patch_kc_client(monkeypatch)

        payload = {
            "username": "dbcheck",
            "password": "secret123",
            "full_name": "DB Check",
            "role": "student",
        }
        resp = await client.post("/api/custom/auth/register", json=payload)
        assert resp.status_code == 201, resp.text

        user_id = resp.json()["user_id"]

        users_resp = await client.get("/api/custom/users")
        assert users_resp.status_code == 200
        all_users = users_resp.json()
        user_ids = [str(u["id"]) for u in all_users]
        assert user_id in user_ids, f"User {user_id} not found in DB"
