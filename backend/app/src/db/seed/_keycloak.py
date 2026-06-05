"""Create test users in Keycloak, return dict of real UUIDs.

Called at the start of seed_database() so that user rows in the
application database use the same UUIDs that Keycloak assigns.
"""

import uuid

import httpx
from core.config import settings
from db.seed.constants import (
    FALLBACK_UUIDS,
    KEY_CHEMISTRY_TUTOR,
    KEY_ENGLISH_TUTOR,
    KEY_MATH_1,
    KEY_MATH_2,
    KEY_MATH_3,
    KEY_MATH_4,
    KEY_MATH_5,
    KEY_PHYSICS_TUTOR,
    KEY_RUSSIAN_TUTOR,
    KEY_STUDENT_NEW1,
    KEY_STUDENT_NEW2,
    KEY_STUDENT_OLGA,
    KEY_STUDENT_TATIANA,
    KEY_SUD_STUDENT,
)

_SEED_USERS: list[dict] = [
    # ── Login: teach / pass ── Russian tutor with 5 students ──
    {
        "key": KEY_RUSSIAN_TUTOR,
        "username": "teach",
        "email": "anna.petrova@example.com",
        "role": "tutor",
        "password": "pass",
    },
    # ── Login: sud / pass ── Student with 5 subject tutors ──
    {
        "key": KEY_SUD_STUDENT,
        "username": "sud",
        "email": "dmitry.kozlov@example.com",
        "role": "student",
        "password": "pass",
    },
    # ── Math tutors (5) ────────────────────────────────────
    {
        "key": KEY_MATH_1,
        "username": "ivan.ivanov",
        "email": "ivan.ivanov@example.com",
        "role": "tutor",
        "password": "password",
    },
    {
        "key": KEY_MATH_2,
        "username": "alex.sidorov",
        "email": "alex.sidorov@example.com",
        "role": "tutor",
        "password": "password",
    },
    {
        "key": KEY_MATH_3,
        "username": "dmitry.math3",
        "email": "dmitry.math3@example.com",
        "role": "tutor",
        "password": "password",
    },
    {
        "key": KEY_MATH_4,
        "username": "olga.math4",
        "email": "olga.math4@example.com",
        "role": "tutor",
        "password": "password",
    },
    {
        "key": KEY_MATH_5,
        "username": "sergey.math5",
        "email": "sergey.math5@example.com",
        "role": "tutor",
        "password": "password",
    },
    # ── Other tutors ───────────────────────────────────────
    {
        "key": KEY_CHEMISTRY_TUTOR,
        "username": "elena.kuznecova",
        "email": "elena.kuznecova@example.com",
        "role": "tutor",
        "password": "password",
    },
    {
        "key": KEY_PHYSICS_TUTOR,
        "username": "petr.fizikov",
        "email": "petr.fizikov@example.com",
        "role": "tutor",
        "password": "password",
    },
    {
        "key": KEY_ENGLISH_TUTOR,
        "username": "irina.english",
        "email": "irina.english@example.com",
        "role": "tutor",
        "password": "password",
    },
    # ── Other students ─────────────────────────────────────
    {
        "key": KEY_STUDENT_OLGA,
        "username": "olga.smirnova",
        "email": "olga.smirnova@example.com",
        "role": "student",
        "password": "password",
    },
    {
        "key": KEY_STUDENT_TATIANA,
        "username": "tatiana.novikova",
        "email": "tatiana.novikova@example.com",
        "role": "student",
        "password": "password",
    },
    {
        "key": KEY_STUDENT_NEW1,
        "username": "alexey.student1",
        "email": "alexey.student1@example.com",
        "role": "student",
        "password": "password",
    },
    {
        "key": KEY_STUDENT_NEW2,
        "username": "maria.student2",
        "email": "maria.student2@example.com",
        "role": "student",
        "password": "password",
    },
]


async def seed_keycloak_users() -> dict[str, uuid.UUID]:
    """Create seed users in Keycloak & return {key: real_uuid}."""
    keycloak_url = settings.KEYCLOAK_URL.rstrip("/")
    realm = "tutorapp"
    admin_user = "admin"
    admin_password = "admin"

    result: dict[str, uuid.UUID] = {}

    print("Seed: creating Keycloak test users …")

    try:
        async with httpx.AsyncClient(base_url=keycloak_url, timeout=30.0) as client:
            # ── 1. Get admin token ───────────────────────────────
            token_resp = await client.post(
                "/realms/master/protocol/openid-connect/token",
                data={
                    "client_id": "admin-cli",
                    "username": admin_user,
                    "password": admin_password,
                    "grant_type": "password",
                },
            )
            token_resp.raise_for_status()
            token = token_resp.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}

            # ── 2. Fetch realm role definitions ──────────────────
            roles_resp = await client.get(
                f"/admin/realms/{realm}/roles", headers=headers
            )
            roles_resp.raise_for_status()
            roles_by_name: dict[str, dict] = {r["name"]: r for r in roles_resp.json()}

            # ── 3. Resolve existing users ────────────────────────
            existing_resp = await client.get(
                f"/admin/realms/{realm}/users", headers=headers, params={"max": 100}
            )
            existing_resp.raise_for_status()
            existing_by_username: dict[str, dict] = {
                u["username"]: u for u in existing_resp.json()
            }

            # ── 4. Ensure every user exists ──────────────────────
            for u in _SEED_USERS:
                username = u["username"]
                existing = existing_by_username.get(username)

                if existing:
                    # Already exists — use its Keycloak-assigned id
                    kc_id = existing["id"]
                    print(
                        f"  Keycloak: {username} already exists (id={kc_id}) — keeping"
                    )
                else:
                    # Create with ANY id that Keycloak assigns
                    user_payload = {
                        "username": username,
                        "email": u["email"],
                        "emailVerified": True,
                        "enabled": True,
                    }
                    create_resp = await client.post(
                        f"/admin/realms/{realm}/users",
                        json=user_payload,
                        headers=headers,
                    )
                    create_resp.raise_for_status()

                    # Extract Keycloak-assigned UUID from Location header
                    location = create_resp.headers.get("location", "")
                    kc_id = location.rsplit("/", 1)[-1] if location else ""

                    if not kc_id:
                        lookup = await client.get(
                            f"/admin/realms/{realm}/users",
                            params={"username": username},
                            headers=headers,
                        )
                        lookup.raise_for_status()
                        kc_id = lookup.json()[0]["id"]

                    print(f"  Keycloak: created {username} (id={kc_id})")

                    # Set password
                    await client.put(
                        f"/admin/realms/{realm}/users/{kc_id}/reset-password",
                        json={
                            "type": "password",
                            "value": u["password"],
                            "temporary": False,
                        },
                        headers=headers,
                    )

                    # Assign realm role
                    role = roles_by_name.get(u["role"])
                    if role:
                        await client.post(
                            f"/admin/realms/{realm}/users/{kc_id}/role-mappings/realm",
                            json=[{"id": role["id"], "name": role["name"]}],
                            headers=headers,
                        )

                result[u["key"]] = uuid.UUID(kc_id)

        print("Seed: Keycloak test users ready.")
        return result

    except httpx.ConnectError:
        print(
            "  ⚠  Keycloak not reachable — using fallback UUIDs. "
            "JWT tokens will NOT match database user IDs."
        )
        return dict(FALLBACK_UUIDS)
    except Exception as exc:
        print(f"  ⚠  Keycloak seed failed: {exc}")
        print("  Using fallback UUIDs.")
        return dict(FALLBACK_UUIDS)
