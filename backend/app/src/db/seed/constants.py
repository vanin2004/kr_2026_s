"""Seed database — constants.

Subjects, tags, test library, and fallback UUIDs.
Real user UUIDs come from Keycloak at seed time.
"""

import uuid
from datetime import datetime, timezone

# ── Keys for the user_uuid dict returned by seed_keycloak_users() ──
KEY_RUSSIAN_TUTOR = "russian_tutor"  # Anna → login: teach
KEY_SUD_STUDENT = "sud_student"  # Dmitry → login: sud

KEY_MATH_1 = "math_1"  # Ivan
KEY_MATH_2 = "math_2"  # Alex
KEY_MATH_3 = "math_3"  # Zaitsev (young)
KEY_MATH_4 = "math_4"  # Sokolova (strict)
KEY_MATH_5 = "math_5"  # Morozov (experienced)

KEY_CHEMISTRY_TUTOR = "chemistry_tutor"
KEY_PHYSICS_TUTOR = "physics_tutor"
KEY_ENGLISH_TUTOR = "english_tutor"

KEY_STUDENT_OLGA = "student_olga"
KEY_STUDENT_TATIANA = "student_tatiana"
KEY_STUDENT_NEW1 = "student_new1"
KEY_STUDENT_NEW2 = "student_new2"

# ── All keys for iteration ─────────────────────────────────────
ALL_USER_KEYS: list[str] = [
    KEY_RUSSIAN_TUTOR,
    KEY_SUD_STUDENT,
    KEY_MATH_1,
    KEY_MATH_2,
    KEY_MATH_3,
    KEY_MATH_4,
    KEY_MATH_5,
    KEY_CHEMISTRY_TUTOR,
    KEY_PHYSICS_TUTOR,
    KEY_ENGLISH_TUTOR,
    KEY_STUDENT_OLGA,
    KEY_STUDENT_TATIANA,
    KEY_STUDENT_NEW1,
    KEY_STUDENT_NEW2,
]

# ── Fallback deterministic UUIDs (used when Keycloak is down) ──
FALLBACK_UUIDS: dict[str, uuid.UUID] = {
    KEY_RUSSIAN_TUTOR: uuid.UUID("22222222-2222-2222-2222-222222222222"),
    KEY_SUD_STUDENT: uuid.UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"),
    KEY_MATH_1: uuid.UUID("11111111-1111-1111-1111-111111111111"),
    KEY_MATH_2: uuid.UUID("33333333-3333-3333-3333-333333333333"),
    KEY_MATH_3: uuid.UUID("77777777-7777-7777-7777-777777777777"),
    KEY_MATH_4: uuid.UUID("88888888-8888-8888-8888-888888888888"),
    KEY_MATH_5: uuid.UUID("99999999-9999-9999-9999-999999999999"),
    KEY_CHEMISTRY_TUTOR: uuid.UUID("44444444-4444-4444-4444-444444444444"),
    KEY_PHYSICS_TUTOR: uuid.UUID("55555555-5555-5555-5555-555555555555"),
    KEY_ENGLISH_TUTOR: uuid.UUID("66666666-6666-6666-6666-666666666666"),
    KEY_STUDENT_OLGA: uuid.UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
    KEY_STUDENT_TATIANA: uuid.UUID("cccccccc-cccc-cccc-cccc-cccccccccccc"),
    KEY_STUDENT_NEW1: uuid.UUID("dddddddd-dddd-dddd-dddd-dddddddddddd"),
    KEY_STUDENT_NEW2: uuid.UUID("eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee"),
}

# ── Fixed deterministic UUIDs for subjects ───────────────────
SUBJ_MATH = uuid.UUID("10000001-0000-0000-0000-000000000001")
SUBJ_PHYSICS = uuid.UUID("10000001-0000-0000-0000-000000000002")
SUBJ_RUSSIAN = uuid.UUID("10000001-0000-0000-0000-000000000003")
SUBJ_ENGLISH = uuid.UUID("10000001-0000-0000-0000-000000000004")
SUBJ_CHEMISTRY = uuid.UUID("10000001-0000-0000-0000-000000000005")
SUBJ_HISTORY = uuid.UUID("10000001-0000-0000-0000-000000000006")

# ── Fixed deterministic UUIDs for tags ──────────────────────
TAG_PATIENT = uuid.UUID("20000001-0000-0000-0000-000000000001")
TAG_INTERACTIVE = uuid.UUID("20000001-0000-0000-0000-000000000002")
TAG_STRICT = uuid.UUID("20000001-0000-0000-0000-000000000003")
TAG_EXPERIENCED = uuid.UUID("20000001-0000-0000-0000-000000000004")
TAG_YOUNG = uuid.UUID("20000001-0000-0000-0000-000000000005")
TAG_REMOTE = uuid.UUID("20000001-0000-0000-0000-000000000006")
TAG_INDIVIDUAL = uuid.UUID("20000001-0000-0000-0000-000000000007")
TAG_EGE = uuid.UUID("20000001-0000-0000-0000-000000000008")

# ── Fixed deterministic UUIDs for test_library ─────────────
TEST_LIB_1_ID = uuid.UUID("30000001-0000-0000-0000-000000000001")
TEST_LIB_2_ID = uuid.UUID("30000001-0000-0000-0000-000000000002")
TEST_LIB_3_ID = uuid.UUID("30000001-0000-0000-0000-000000000003")

# ── Timestamp anchor ────────────────────────────────────────
NOW = datetime.now(timezone.utc)
