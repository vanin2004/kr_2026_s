"""Registration endpoint.

Creates a user in both Keycloak (for authentication) and the local
Postgres database (for application data and profiles).
"""

import logging
import uuid

import httpx
from core.config import settings
from db.session import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from models.enums import UserRole
from models.tables import StudentProfile, Subject, TutorProfile, User
from schemas.api.auth import RegisterRequest, RegisterResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()
logger = logging.getLogger(__name__)

KEYCLOAK_URL = settings.KEYCLOAK_URL.rstrip("/")
KEYCLOAK_REALM = settings.KEYCLOAK_REALM
ADMIN_USER = settings.KEYCLOAK_ADMIN_USER
ADMIN_PASSWORD = settings.KEYCLOAK_ADMIN_PASSWORD


async def _kc_admin_token(client: httpx.AsyncClient) -> str:
    """Obtain a Keycloak admin access token."""
    resp = await client.post(
        "/realms/master/protocol/openid-connect/token",
        data={
            "client_id": "admin-cli",
            "username": ADMIN_USER,
            "password": ADMIN_PASSWORD,
            "grant_type": "password",
        },
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


async def _kc_role_id(
    client: httpx.AsyncClient,
    token: str,
    role_name: str,
) -> dict | None:
    """Fetch realm roles and return the one matching *role_name*."""
    resp = await client.get(
        f"/admin/realms/{KEYCLOAK_REALM}/roles",
        headers={"Authorization": f"Bearer {token}"},
    )
    resp.raise_for_status()
    for r in resp.json():
        if r["name"] == role_name:
            return {"id": r["id"], "name": r["name"]}
    return None


async def _kc_user_exists(
    client: httpx.AsyncClient,
    token: str,
    username: str,
) -> bool:
    """Return True if a Keycloak user with *username* already exists."""
    resp = await client.get(
        f"/admin/realms/{KEYCLOAK_REALM}/users",
        params={"username": username},
        headers={"Authorization": f"Bearer {token}"},
    )
    resp.raise_for_status()
    return len(resp.json()) > 0


@router.post(
    "/auth/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    data: RegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> RegisterResponse:
    """Register a new user (tutor or student).

    Steps
    -----
    1. Validate input and check username availability in Keycloak
    2. Create the user in Keycloak (authentication)
    3. Create User + profile row in the local database
    """
    email = f"{data.username}@tutorapp.local"
    user_uuid = uuid.uuid4()

    # ── Check Keycloak for duplicate username ──────────────────────
    try:
        async with httpx.AsyncClient(base_url=KEYCLOAK_URL, timeout=15.0) as client:
            token = await _kc_admin_token(client)

            if await _kc_user_exists(client, token, data.username):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Username '{data.username}' is already taken",
                )

            # ── Create user in Keycloak ────────────────────────────
            payload = {
                "id": str(user_uuid),
                "username": data.username,
                "email": email,
                "emailVerified": True,
                "enabled": True,
            }
            create_resp = await client.post(
                f"/admin/realms/{KEYCLOAK_REALM}/users",
                json=payload,
                headers={"Authorization": f"Bearer {token}"},
            )
            create_resp.raise_for_status()

            # Determine the actual Keycloak-assigned ID
            location = create_resp.headers.get("location", "")
            kc_id = location.rsplit("/", 1)[-1] if location else str(user_uuid)

            # Set password
            await client.put(
                f"/admin/realms/{KEYCLOAK_REALM}/users/{kc_id}/reset-password",
                json={
                    "type": "password",
                    "value": data.password,
                    "temporary": False,
                },
                headers={"Authorization": f"Bearer {token}"},
            )

            # Assign realm role
            role_info = await _kc_role_id(client, token, data.role)
            if role_info:
                await client.post(
                    f"/admin/realms/{KEYCLOAK_REALM}/users/{kc_id}/role-mappings/realm",
                    json=[role_info],
                    headers={"Authorization": f"Bearer {token}"},
                )

    except httpx.HTTPStatusError as exc:
        logger.error("Keycloak HTTP error: %s", exc.response.text)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Registration service unavailable, please try again later",
        )
    except httpx.ConnectError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Registration service unavailable, please try again later",
        )

    # ── Create local database records ──────────────────────────────
    try:
        role = UserRole(data.role)
    except ValueError:
        # Should not happen – already validated by pydantic
        raise HTTPException(status_code=400, detail=f"Invalid role: {data.role}")

    db_user = User(id=user_uuid, email=email, role=role)
    db.add(db_user)

    if role == UserRole.tutor:
        # Validate subject exists
        if data.subject_id:
            subject = await db.execute(
                select(Subject).where(Subject.id == data.subject_id)
            )
            if not subject.scalar_one_or_none():
                # Roll back Keycloak user
                try:
                    async with httpx.AsyncClient(
                        base_url=KEYCLOAK_URL, timeout=10.0
                    ) as cl:
                        t = await _kc_admin_token(cl)
                        await cl.delete(
                            f"/admin/realms/{KEYCLOAK_REALM}/users/{user_uuid}",
                            headers={"Authorization": f"Bearer {t}"},
                        )
                except Exception:
                    logger.warning("Failed to clean up Keycloak user %s", user_uuid)
                raise HTTPException(
                    status_code=400,
                    detail=f"Subject '{data.subject_id}' not found",
                )

        db.add(
            TutorProfile(
                user_id=user_uuid,
                full_name=data.full_name,
                subject_id=data.subject_id,
                hourly_rate=data.hourly_rate,
            )
        )
    else:
        db.add(
            StudentProfile(
                user_id=user_uuid,
                full_name=data.full_name,
            )
        )

    await db.flush()
    logger.info(
        "User registered: id=%s, username=%s, role=%s",
        user_uuid,
        data.username,
        data.role,
    )

    return RegisterResponse(
        user_id=str(user_uuid),
        username=data.username,
        role=data.role,
    )
