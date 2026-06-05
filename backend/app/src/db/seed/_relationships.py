"""Seed tutor tags, student preferred tags, certifications, and schedules.

Accepts real UUIDs from Keycloak (or fallbacks).
"""

import uuid
from datetime import time

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
    TAG_EGE,
    TAG_EXPERIENCED,
    TAG_INDIVIDUAL,
    TAG_INTERACTIVE,
    TAG_PATIENT,
    TAG_REMOTE,
    TAG_STRICT,
    TAG_YOUNG,
)
from models.tables import (
    Schedule,
    StudentPreferredTag,
    TutorCertification,
    TutorTag,
)
from sqlalchemy.ext.asyncio import AsyncSession


def seed_relationships(session: AsyncSession, u: dict[str, uuid.UUID]) -> None:
    # ── Tutor Tags ────────────────────────────────────────────
    tutor_tags = [
        # Russian — интерактивный, дистанционно, инд. подход
        TutorTag(tutor_id=u[KEY_RUSSIAN_TUTOR], tag_id=TAG_INTERACTIVE),
        TutorTag(tutor_id=u[KEY_RUSSIAN_TUTOR], tag_id=TAG_REMOTE),
        TutorTag(tutor_id=u[KEY_RUSSIAN_TUTOR], tag_id=TAG_INDIVIDUAL),
        # Math #1 — опытный, терпеливый, ЕГЭ
        TutorTag(tutor_id=u[KEY_MATH_1], tag_id=TAG_PATIENT),
        TutorTag(tutor_id=u[KEY_MATH_1], tag_id=TAG_EXPERIENCED),
        TutorTag(tutor_id=u[KEY_MATH_1], tag_id=TAG_EGE),
        # Math #2 — строгий, опытный, ЕГЭ
        TutorTag(tutor_id=u[KEY_MATH_2], tag_id=TAG_STRICT),
        TutorTag(tutor_id=u[KEY_MATH_2], tag_id=TAG_EXPERIENCED),
        TutorTag(tutor_id=u[KEY_MATH_2], tag_id=TAG_EGE),
        # Math #3 — молодой, интерактивный
        TutorTag(tutor_id=u[KEY_MATH_3], tag_id=TAG_YOUNG),
        TutorTag(tutor_id=u[KEY_MATH_3], tag_id=TAG_INTERACTIVE),
        # Math #4 — строгий, ЕГЭ, инд. подход
        TutorTag(tutor_id=u[KEY_MATH_4], tag_id=TAG_STRICT),
        TutorTag(tutor_id=u[KEY_MATH_4], tag_id=TAG_EGE),
        TutorTag(tutor_id=u[KEY_MATH_4], tag_id=TAG_INDIVIDUAL),
        # Math #5 — опытный, ЕГЭ
        TutorTag(tutor_id=u[KEY_MATH_5], tag_id=TAG_EXPERIENCED),
        TutorTag(tutor_id=u[KEY_MATH_5], tag_id=TAG_EGE),
        # Chemistry — молодой, дистанционно
        TutorTag(tutor_id=u[KEY_CHEMISTRY_TUTOR], tag_id=TAG_YOUNG),
        TutorTag(tutor_id=u[KEY_CHEMISTRY_TUTOR], tag_id=TAG_REMOTE),
        # Physics — молодой, интерактивный, дистанционно
        TutorTag(tutor_id=u[KEY_PHYSICS_TUTOR], tag_id=TAG_YOUNG),
        TutorTag(tutor_id=u[KEY_PHYSICS_TUTOR], tag_id=TAG_INTERACTIVE),
        TutorTag(tutor_id=u[KEY_PHYSICS_TUTOR], tag_id=TAG_REMOTE),
        # English — дистанционно, инд. подход
        TutorTag(tutor_id=u[KEY_ENGLISH_TUTOR], tag_id=TAG_REMOTE),
        TutorTag(tutor_id=u[KEY_ENGLISH_TUTOR], tag_id=TAG_INDIVIDUAL),
    ]
    session.add_all(tutor_tags)

    # ── Student Preferred Tags ────────────────────────────────
    student_tags = [
        StudentPreferredTag(
            student_id=u[KEY_STUDENT_OLGA], tag_id=TAG_EXPERIENCED, is_required=True
        ),
        StudentPreferredTag(
            student_id=u[KEY_STUDENT_OLGA], tag_id=TAG_INDIVIDUAL, is_required=False
        ),
        StudentPreferredTag(
            student_id=u[KEY_SUD_STUDENT], tag_id=TAG_STRICT, is_required=False
        ),
        StudentPreferredTag(
            student_id=u[KEY_SUD_STUDENT], tag_id=TAG_EGE, is_required=True
        ),
        StudentPreferredTag(
            student_id=u[KEY_STUDENT_TATIANA], tag_id=TAG_INTERACTIVE, is_required=False
        ),
        StudentPreferredTag(
            student_id=u[KEY_STUDENT_TATIANA], tag_id=TAG_YOUNG, is_required=False
        ),
        StudentPreferredTag(
            student_id=u[KEY_STUDENT_NEW1], tag_id=TAG_PATIENT, is_required=True
        ),
        StudentPreferredTag(
            student_id=u[KEY_STUDENT_NEW1], tag_id=TAG_REMOTE, is_required=False
        ),
        StudentPreferredTag(
            student_id=u[KEY_STUDENT_NEW2], tag_id=TAG_EXPERIENCED, is_required=False
        ),
        StudentPreferredTag(
            student_id=u[KEY_STUDENT_NEW2], tag_id=TAG_INDIVIDUAL, is_required=False
        ),
    ]
    session.add_all(student_tags)

    # ── Certifications ────────────────────────────────────────
    certs = [
        TutorCertification(
            tutor_id=u[KEY_RUSSIAN_TUTOR],
            title="Диплом с отличием РГПУ им. Герцена",
            file_url="https://example.com/certs/anna_diploma.pdf",
            is_verified=True,
        ),
        TutorCertification(
            tutor_id=u[KEY_MATH_1],
            title="Кандидат физико-математических наук",
            file_url="https://example.com/certs/ivan_phd.pdf",
            is_verified=True,
        ),
        TutorCertification(
            tutor_id=u[KEY_MATH_1],
            title="Сертификат эксперта ЕГЭ по математике",
            file_url="https://example.com/certs/ivan_ege.pdf",
            is_verified=True,
        ),
        TutorCertification(
            tutor_id=u[KEY_MATH_2],
            title="Сертификат эксперта ЕГЭ по математике",
            file_url="https://example.com/certs/alex_ege.pdf",
            is_verified=True,
        ),
        TutorCertification(
            tutor_id=u[KEY_MATH_4],
            title="Сертификат эксперта ЕГЭ по математике",
            file_url="https://example.com/certs/olga_ege.pdf",
            is_verified=True,
        ),
        TutorCertification(
            tutor_id=u[KEY_MATH_5],
            title="Доктор физико-математических наук",
            file_url="https://example.com/certs/sergey_doc.pdf",
            is_verified=True,
        ),
        TutorCertification(
            tutor_id=u[KEY_PHYSICS_TUTOR],
            title="Сертификат олимпиадного тренера",
            file_url="https://example.com/certs/peter_olymp.pdf",
            is_verified=False,
        ),
        TutorCertification(
            tutor_id=u[KEY_ENGLISH_TUTOR],
            title="Диплом МГЛУ с отличием",
            file_url="https://example.com/certs/irina_diploma.pdf",
            is_verified=True,
        ),
    ]
    session.add_all(certs)

    # ── Schedules ─────────────────────────────────────────────
    schedules = [
        # Russian tutor — Вт, Чт, Сб
        Schedule(
            tutor_id=u[KEY_RUSSIAN_TUTOR],
            day_of_week=2,
            start_time=time(12, 0),
            end_time=time(20, 0),
        ),
        Schedule(
            tutor_id=u[KEY_RUSSIAN_TUTOR],
            day_of_week=4,
            start_time=time(12, 0),
            end_time=time(20, 0),
        ),
        Schedule(
            tutor_id=u[KEY_RUSSIAN_TUTOR],
            day_of_week=6,
            start_time=time(10, 0),
            end_time=time(14, 0),
        ),
        # Math #1 — Пн, Ср, Пт
        Schedule(
            tutor_id=u[KEY_MATH_1],
            day_of_week=1,
            start_time=time(10, 0),
            end_time=time(18, 0),
        ),
        Schedule(
            tutor_id=u[KEY_MATH_1],
            day_of_week=3,
            start_time=time(10, 0),
            end_time=time(18, 0),
        ),
        Schedule(
            tutor_id=u[KEY_MATH_1],
            day_of_week=5,
            start_time=time(10, 0),
            end_time=time(16, 0),
        ),
        # Math #2 — Пн-Пт
        Schedule(
            tutor_id=u[KEY_MATH_2],
            day_of_week=1,
            start_time=time(9, 0),
            end_time=time(15, 0),
        ),
        Schedule(
            tutor_id=u[KEY_MATH_2],
            day_of_week=2,
            start_time=time(9, 0),
            end_time=time(15, 0),
        ),
        Schedule(
            tutor_id=u[KEY_MATH_2],
            day_of_week=3,
            start_time=time(9, 0),
            end_time=time(15, 0),
        ),
        Schedule(
            tutor_id=u[KEY_MATH_2],
            day_of_week=4,
            start_time=time(9, 0),
            end_time=time(15, 0),
        ),
        Schedule(
            tutor_id=u[KEY_MATH_2],
            day_of_week=5,
            start_time=time(9, 0),
            end_time=time(15, 0),
        ),
        # Math #3 — Пн, Ср, Пт (вечер)
        Schedule(
            tutor_id=u[KEY_MATH_3],
            day_of_week=1,
            start_time=time(17, 0),
            end_time=time(22, 0),
        ),
        Schedule(
            tutor_id=u[KEY_MATH_3],
            day_of_week=3,
            start_time=time(17, 0),
            end_time=time(22, 0),
        ),
        Schedule(
            tutor_id=u[KEY_MATH_3],
            day_of_week=5,
            start_time=time(17, 0),
            end_time=time(22, 0),
        ),
        # Math #4 — Вт, Чт, Сб
        Schedule(
            tutor_id=u[KEY_MATH_4],
            day_of_week=2,
            start_time=time(9, 0),
            end_time=time(16, 0),
        ),
        Schedule(
            tutor_id=u[KEY_MATH_4],
            day_of_week=4,
            start_time=time(9, 0),
            end_time=time(16, 0),
        ),
        Schedule(
            tutor_id=u[KEY_MATH_4],
            day_of_week=6,
            start_time=time(10, 0),
            end_time=time(15, 0),
        ),
        # Math #5 — Пн-Пт (утро)
        Schedule(
            tutor_id=u[KEY_MATH_5],
            day_of_week=1,
            start_time=time(8, 0),
            end_time=time(14, 0),
        ),
        Schedule(
            tutor_id=u[KEY_MATH_5],
            day_of_week=2,
            start_time=time(8, 0),
            end_time=time(14, 0),
        ),
        Schedule(
            tutor_id=u[KEY_MATH_5],
            day_of_week=3,
            start_time=time(8, 0),
            end_time=time(14, 0),
        ),
        Schedule(
            tutor_id=u[KEY_MATH_5],
            day_of_week=4,
            start_time=time(8, 0),
            end_time=time(14, 0),
        ),
        Schedule(
            tutor_id=u[KEY_MATH_5],
            day_of_week=5,
            start_time=time(8, 0),
            end_time=time(14, 0),
        ),
        # Chemistry — Ср
        Schedule(
            tutor_id=u[KEY_CHEMISTRY_TUTOR],
            day_of_week=3,
            start_time=time(14, 0),
            end_time=time(20, 0),
        ),
        # Physics — Пн, Ср
        Schedule(
            tutor_id=u[KEY_PHYSICS_TUTOR],
            day_of_week=1,
            start_time=time(15, 0),
            end_time=time(21, 0),
        ),
        Schedule(
            tutor_id=u[KEY_PHYSICS_TUTOR],
            day_of_week=3,
            start_time=time(15, 0),
            end_time=time(21, 0),
        ),
        # English — Вт, Чт
        Schedule(
            tutor_id=u[KEY_ENGLISH_TUTOR],
            day_of_week=2,
            start_time=time(10, 0),
            end_time=time(17, 0),
        ),
        Schedule(
            tutor_id=u[KEY_ENGLISH_TUTOR],
            day_of_week=4,
            start_time=time(10, 0),
            end_time=time(17, 0),
        ),
    ]
    session.add_all(schedules)
