"""Seed users, tutor profiles and student profiles.

Accepts real UUIDs from Keycloak (or fallbacks).
"""

import uuid
from datetime import timedelta

from db.seed.constants import (
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
    NOW,
    SUBJ_CHEMISTRY,
    SUBJ_ENGLISH,
    SUBJ_MATH,
    SUBJ_PHYSICS,
    SUBJ_RUSSIAN,
)
from models.enums import UserRole
from models.tables import StudentProfile, TutorProfile, User
from sqlalchemy.ext.asyncio import AsyncSession


def seed_users(session: AsyncSession, u: dict[str, uuid.UUID]) -> None:
    users = [
        # ── Russian tutor (login: teach) ─────────────────────
        User(
            id=u[KEY_RUSSIAN_TUTOR],
            email="anna.petrova@example.com",
            role=UserRole.tutor,
            created_at=NOW - timedelta(days=90),
        ),
        # ── Student sud (login: sud) ──────────────────────────
        User(
            id=u[KEY_SUD_STUDENT],
            email="dmitry.kozlov@example.com",
            role=UserRole.student,
            created_at=NOW - timedelta(days=60),
        ),
        # ── Math tutors (5) ───────────────────────────────────
        User(
            id=u[KEY_MATH_1],
            email="ivan.ivanov@example.com",
            role=UserRole.tutor,
            created_at=NOW - timedelta(days=120),
        ),
        User(
            id=u[KEY_MATH_2],
            email="alex.sidorov@example.com",
            role=UserRole.tutor,
            created_at=NOW - timedelta(days=180),
        ),
        User(
            id=u[KEY_MATH_3],
            email="dmitry.math3@example.com",
            role=UserRole.tutor,
            created_at=NOW - timedelta(days=20),
        ),
        User(
            id=u[KEY_MATH_4],
            email="olga.math4@example.com",
            role=UserRole.tutor,
            created_at=NOW - timedelta(days=200),
        ),
        User(
            id=u[KEY_MATH_5],
            email="sergey.math5@example.com",
            role=UserRole.tutor,
            created_at=NOW - timedelta(days=365),
        ),
        # ── Other tutors ──────────────────────────────────────
        User(
            id=u[KEY_CHEMISTRY_TUTOR],
            email="elena.kuznecova@example.com",
            role=UserRole.tutor,
            created_at=NOW - timedelta(days=30),
        ),
        User(
            id=u[KEY_PHYSICS_TUTOR],
            email="petr.fizikov@example.com",
            role=UserRole.tutor,
            created_at=NOW - timedelta(days=60),
        ),
        User(
            id=u[KEY_ENGLISH_TUTOR],
            email="irina.english@example.com",
            role=UserRole.tutor,
            created_at=NOW - timedelta(days=45),
        ),
        # ── Other students (Anna's pupils) ────────────────────
        User(
            id=u[KEY_STUDENT_OLGA],
            email="olga.smirnova@example.com",
            role=UserRole.student,
            created_at=NOW - timedelta(days=60),
        ),
        User(
            id=u[KEY_STUDENT_TATIANA],
            email="tatiana.novikova@example.com",
            role=UserRole.student,
            created_at=NOW - timedelta(days=60),
        ),
        User(
            id=u[KEY_STUDENT_NEW1],
            email="alexey.student1@example.com",
            role=UserRole.student,
            created_at=NOW - timedelta(days=40),
        ),
        User(
            id=u[KEY_STUDENT_NEW2],
            email="maria.student2@example.com",
            role=UserRole.student,
            created_at=NOW - timedelta(days=35),
        ),
    ]
    session.add_all(users)

    tutor_profiles = [
        # ── Russian tutor: Анна ──────────────────────────────
        TutorProfile(
            user_id=u[KEY_RUSSIAN_TUTOR],
            full_name="Петрова Анна Сергеевна",
            photo_url="https://i.pravatar.cc/150?u=anna",
            education="РГПУ им. Герцена, филологический факультет",
            subject_id=SUBJ_RUSSIAN,
            hourly_rate=1200,
            experience_years=5,
            is_verified=True,
            student_count=30,
            rating_efficiency=4.600,
            rating_communication=4.800,
            rating_expertise=4.500,
            rating_responsiveness=4.900,
            is_new_boost=False,
        ),
        # ── Math #1: Иван (опытный, терпеливый) ──────────────
        TutorProfile(
            user_id=u[KEY_MATH_1],
            full_name="Иванов Иван Иванович",
            photo_url="https://i.pravatar.cc/150?u=ivan",
            education="МГУ им. Ломоносова, механико-математический факультет",
            subject_id=SUBJ_MATH,
            hourly_rate=1500,
            experience_years=8,
            is_verified=True,
            student_count=45,
            rating_efficiency=4.800,
            rating_communication=4.500,
            rating_expertise=4.900,
            rating_responsiveness=4.700,
            is_new_boost=False,
        ),
        # ── Math #2: Алексей (строгий, опытный) ──────────────
        TutorProfile(
            user_id=u[KEY_MATH_2],
            full_name="Сидоров Алексей Петрович",
            photo_url="https://i.pravatar.cc/150?u=alex",
            education="МФТИ, факультет общей и прикладной физики",
            subject_id=SUBJ_MATH,
            hourly_rate=2000,
            experience_years=12,
            is_verified=True,
            student_count=78,
            rating_efficiency=4.950,
            rating_communication=4.200,
            rating_expertise=4.980,
            rating_responsiveness=4.300,
            is_new_boost=False,
        ),
        # ── Math #3: Дмитрий (молодой, интерактивный) ────────
        TutorProfile(
            user_id=u[KEY_MATH_3],
            full_name="Зайцев Дмитрий Олегович",
            photo_url="https://i.pravatar.cc/150?u=dmitry-math",
            education="НИУ ВШЭ, факультет математики",
            subject_id=SUBJ_MATH,
            hourly_rate=800,
            experience_years=1,
            is_verified=False,
            student_count=5,
            rating_efficiency=None,
            rating_communication=None,
            rating_expertise=None,
            rating_responsiveness=None,
            is_new_boost=True,
        ),
        # ── Math #4: Ольга (строгая, ЕГЭ, инд. подход) ───────
        TutorProfile(
            user_id=u[KEY_MATH_4],
            full_name="Соколова Ольга Владимировна",
            photo_url="https://i.pravatar.cc/150?u=olga-math",
            education="МГУ им. Ломоносова, ВМК",
            subject_id=SUBJ_MATH,
            hourly_rate=1800,
            experience_years=6,
            is_verified=True,
            student_count=40,
            rating_efficiency=4.700,
            rating_communication=4.300,
            rating_expertise=4.800,
            rating_responsiveness=4.200,
            is_new_boost=False,
        ),
        # ── Math #5: Сергей (супер-опытный, ЕГЭ) ─────────────
        TutorProfile(
            user_id=u[KEY_MATH_5],
            full_name="Морозов Сергей Николаевич",
            photo_url="https://i.pravatar.cc/150?u=sergey-math",
            education="СПбГУ, математико-механический факультет",
            subject_id=SUBJ_MATH,
            hourly_rate=3000,
            experience_years=15,
            is_verified=True,
            student_count=120,
            rating_efficiency=4.950,
            rating_communication=4.700,
            rating_expertise=4.990,
            rating_responsiveness=4.600,
            is_new_boost=False,
        ),
        # ── Chemistry: Елена ────────────────────────────────
        TutorProfile(
            user_id=u[KEY_CHEMISTRY_TUTOR],
            full_name="Кузнецова Елена Дмитриевна",
            photo_url="https://i.pravatar.cc/150?u=elena",
            education="СПбГУ, химический факультет",
            subject_id=SUBJ_CHEMISTRY,
            hourly_rate=1000,
            experience_years=2,
            is_verified=False,
            student_count=8,
            rating_efficiency=None,
            rating_communication=None,
            rating_expertise=None,
            rating_responsiveness=None,
            is_new_boost=True,
        ),
        # ── Physics: Пётр ────────────────────────────────────
        TutorProfile(
            user_id=u[KEY_PHYSICS_TUTOR],
            full_name="Физиков Пётр Алексеевич",
            photo_url="https://i.pravatar.cc/150?u=peter",
            education="МФТИ, физический факультет",
            subject_id=SUBJ_PHYSICS,
            hourly_rate=1300,
            experience_years=3,
            is_verified=False,
            student_count=15,
            rating_efficiency=4.300,
            rating_communication=4.600,
            rating_expertise=4.200,
            rating_responsiveness=4.500,
            is_new_boost=True,
        ),
        # ── English: Ирина ───────────────────────────────────
        TutorProfile(
            user_id=u[KEY_ENGLISH_TUTOR],
            full_name="Смирнова Ирина Викторовна",
            photo_url="https://i.pravatar.cc/150?u=irina",
            education="МГЛУ, факультет английского языка",
            subject_id=SUBJ_ENGLISH,
            hourly_rate=1400,
            experience_years=6,
            is_verified=True,
            student_count=35,
            rating_efficiency=4.500,
            rating_communication=4.700,
            rating_expertise=4.600,
            rating_responsiveness=4.400,
            is_new_boost=False,
        ),
    ]
    session.add_all(tutor_profiles)

    student_profiles = [
        # ── sud: ученик с 5 преподавателями ──────────────────
        StudentProfile(
            user_id=u[KEY_SUD_STUDENT],
            full_name="Козлов Дмитрий Алексеевич",
            photo_url="https://i.pravatar.cc/150?u=dmitry",
            search_weights={
                "k1_effectiveness": 0.20,
                "k2_communication": 0.25,
                "k3_expertise": 0.15,
                "k4_responsiveness": 0.20,
                "k5_tags": 0.20,
            },
        ),
        StudentProfile(
            user_id=u[KEY_STUDENT_OLGA],
            full_name="Смирнова Ольга Андреевна",
            photo_url="https://i.pravatar.cc/150?u=olga",
            search_weights={
                "k1_effectiveness": 0.30,
                "k2_communication": 0.20,
                "k3_expertise": 0.25,
                "k4_responsiveness": 0.10,
                "k5_tags": 0.15,
            },
        ),
        StudentProfile(
            user_id=u[KEY_STUDENT_TATIANA],
            full_name="Новикова Татьяна Викторовна",
            photo_url="https://i.pravatar.cc/150?u=tatiana",
            search_weights={
                "k1_effectiveness": 0.25,
                "k2_communication": 0.15,
                "k3_expertise": 0.20,
                "k4_responsiveness": 0.15,
                "k5_tags": 0.25,
            },
        ),
        StudentProfile(
            user_id=u[KEY_STUDENT_NEW1],
            full_name="Соколов Алексей Игоревич",
            photo_url="https://i.pravatar.cc/150?u=alexey",
            search_weights={
                "k1_effectiveness": 0.20,
                "k2_communication": 0.30,
                "k3_expertise": 0.20,
                "k4_responsiveness": 0.15,
                "k5_tags": 0.15,
            },
        ),
        StudentProfile(
            user_id=u[KEY_STUDENT_NEW2],
            full_name="Иванова Мария Денисовна",
            photo_url="https://i.pravatar.cc/150?u=maria",
            search_weights={
                "k1_effectiveness": 0.25,
                "k2_communication": 0.20,
                "k3_expertise": 0.25,
                "k4_responsiveness": 0.10,
                "k5_tags": 0.20,
            },
        ),
    ]
    session.add_all(student_profiles)
