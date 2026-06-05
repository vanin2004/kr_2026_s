"""Seed applications, chats, messages, lessons, and reviews.

Only data matching the three required scenarios:
  1) Russian tutor (Anna) ↔ 5 students
  2) Student sud (Dmitry) ↔ 5 tutors
  3) 5 math tutors with reviews
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
    SUBJ_MATH,
    SUBJ_RUSSIAN,
    TEST_LIB_1_ID,
    TEST_LIB_2_ID,
)
from models.enums import ApplicationStatus, LessonStatus
from models.tables import (
    Application,
    Chat,
    Lesson,
    Message,
    Review,
    TestLibrary,
)
from sqlalchemy.ext.asyncio import AsyncSession


async def seed_interactions(session: AsyncSession, u: dict[str, uuid.UUID]) -> None:
    # ── Helper: deterministic UUID generator ──────────────────
    _idx = [0]

    def _uid(prefix: str) -> uuid.UUID:
        _idx[0] += 1
        return uuid.UUID(f"{prefix}{_idx[0]:04x}-0000-0000-0000-000000000000")

    # ═══════════════════════════════════════════════════════════
    # 1. Applications
    # ═══════════════════════════════════════════════════════════
    app_ids: dict[str, uuid.UUID] = {}

    def _app(key: str) -> uuid.UUID:
        uid = _uid("a300")
        app_ids[key] = uid
        return uid

    applications = [
        # ── Scenario 1: Russian tutor ↔ 5 students ────────
        Application(
            id=_app("anna_olga"),
            student_id=u[KEY_STUDENT_OLGA],
            tutor_id=u[KEY_RUSSIAN_TUTOR],
            status=ApplicationStatus.accepted,
            created_at=NOW - timedelta(days=24),
            responded_at=NOW - timedelta(days=22),
        ),
        Application(
            id=_app("anna_tatiana"),
            student_id=u[KEY_STUDENT_TATIANA],
            tutor_id=u[KEY_RUSSIAN_TUTOR],
            status=ApplicationStatus.accepted,
            created_at=NOW - timedelta(days=22),
            responded_at=NOW - timedelta(days=20),
        ),
        Application(
            id=_app("anna_dmitry"),
            student_id=u[KEY_SUD_STUDENT],
            tutor_id=u[KEY_RUSSIAN_TUTOR],
            status=ApplicationStatus.accepted,
            created_at=NOW - timedelta(days=20),
            responded_at=NOW - timedelta(days=18),
        ),
        Application(
            id=_app("anna_new1"),
            student_id=u[KEY_STUDENT_NEW1],
            tutor_id=u[KEY_RUSSIAN_TUTOR],
            status=ApplicationStatus.accepted,
            created_at=NOW - timedelta(days=18),
            responded_at=NOW - timedelta(days=16),
        ),
        Application(
            id=_app("anna_new2"),
            student_id=u[KEY_STUDENT_NEW2],
            tutor_id=u[KEY_RUSSIAN_TUTOR],
            status=ApplicationStatus.accepted,
            created_at=NOW - timedelta(days=16),
            responded_at=NOW - timedelta(days=14),
        ),
        # ── Scenario 2: sud ↔ 4 more tutors (Anna done above) ──
        Application(
            id=_app("dmitry_math1"),
            student_id=u[KEY_SUD_STUDENT],
            tutor_id=u[KEY_MATH_1],
            status=ApplicationStatus.accepted,
            created_at=NOW - timedelta(days=19),
            responded_at=NOW - timedelta(days=17),
        ),
        Application(
            id=_app("dmitry_chemistry"),
            student_id=u[KEY_SUD_STUDENT],
            tutor_id=u[KEY_CHEMISTRY_TUTOR],
            status=ApplicationStatus.accepted,
            created_at=NOW - timedelta(days=17),
            responded_at=NOW - timedelta(days=15),
        ),
        Application(
            id=_app("dmitry_physics"),
            student_id=u[KEY_SUD_STUDENT],
            tutor_id=u[KEY_PHYSICS_TUTOR],
            status=ApplicationStatus.accepted,
            created_at=NOW - timedelta(days=15),
            responded_at=NOW - timedelta(days=13),
        ),
        Application(
            id=_app("dmitry_english"),
            student_id=u[KEY_SUD_STUDENT],
            tutor_id=u[KEY_ENGLISH_TUTOR],
            status=ApplicationStatus.accepted,
            created_at=NOW - timedelta(days=13),
            responded_at=NOW - timedelta(days=11),
        ),
        # ── Scenario 3: apps for math tutor reviews ──────────
        Application(
            id=_app("olga_math2"),
            student_id=u[KEY_STUDENT_OLGA],
            tutor_id=u[KEY_MATH_2],
            status=ApplicationStatus.accepted,
            created_at=NOW - timedelta(days=30),
            responded_at=NOW - timedelta(days=28),
        ),
        Application(
            id=_app("tatiana_math3"),
            student_id=u[KEY_STUDENT_TATIANA],
            tutor_id=u[KEY_MATH_3],
            status=ApplicationStatus.accepted,
            created_at=NOW - timedelta(days=28),
            responded_at=NOW - timedelta(days=26),
        ),
        Application(
            id=_app("new1_math4"),
            student_id=u[KEY_STUDENT_NEW1],
            tutor_id=u[KEY_MATH_4],
            status=ApplicationStatus.accepted,
            created_at=NOW - timedelta(days=26),
            responded_at=NOW - timedelta(days=24),
        ),
        Application(
            id=_app("new2_math5"),
            student_id=u[KEY_STUDENT_NEW2],
            tutor_id=u[KEY_MATH_5],
            status=ApplicationStatus.accepted,
            created_at=NOW - timedelta(days=24),
            responded_at=NOW - timedelta(days=22),
        ),
    ]
    session.add_all(applications)

    # ═══════════════════════════════════════════════════════════
    # 2. Chats  (one per accepted app from scen. 1 & 2 only)
    # ═══════════════════════════════════════════════════════════
    chat_ids: dict[str, uuid.UUID] = {}

    def _chat(key: str) -> uuid.UUID:
        uid = _uid("b300")
        chat_ids[key] = uid
        return uid

    chats = [
        # Scenario 1
        Chat(id=_chat("chat_anna_olga"), application_id=app_ids["anna_olga"]),
        Chat(id=_chat("chat_anna_tatiana"), application_id=app_ids["anna_tatiana"]),
        Chat(id=_chat("chat_anna_dmitry"), application_id=app_ids["anna_dmitry"]),
        Chat(id=_chat("chat_anna_new1"), application_id=app_ids["anna_new1"]),
        Chat(id=_chat("chat_anna_new2"), application_id=app_ids["anna_new2"]),
        # Scenario 2
        Chat(id=_chat("chat_dmitry_math1"), application_id=app_ids["dmitry_math1"]),
        Chat(
            id=_chat("chat_dmitry_chemistry"),
            application_id=app_ids["dmitry_chemistry"],
        ),
        Chat(
            id=_chat("chat_dmitry_physics"),
            application_id=app_ids["dmitry_physics"],
        ),
        Chat(
            id=_chat("chat_dmitry_english"),
            application_id=app_ids["dmitry_english"],
        ),
    ]
    session.add_all(chats)

    # ═══════════════════════════════════════════════════════════
    # 3. Messages
    # ═══════════════════════════════════════════════════════════
    messages = []

    def _msg(chat_key, sender, text, days_ago, hours_ago, is_read=True):
        return Message(
            id=_uid("f300"),
            chat_id=chat_ids[chat_key],
            sender_id=sender,
            text=text,
            created_at=NOW - timedelta(days=days_ago, hours=hours_ago),
            is_read=is_read,
        )

    # ── Anna ↔ Olga ───────────────────────────────────────────
    messages.append(
        _msg(
            "chat_anna_olga",
            u[KEY_STUDENT_OLGA],
            "Здравствуйте, Анна Сергеевна! Хочу подтянуть русский язык.",
            18,
            5,
        )
    )
    messages.append(
        _msg(
            "chat_anna_olga",
            u[KEY_RUSSIAN_TUTOR],
            "Добрый день, Ольга! С удовольствием помогу. Какие темы вас интересуют?",
            18,
            4,
        )
    )
    messages.append(
        _msg(
            "chat_anna_olga",
            u[KEY_STUDENT_OLGA],
            "Подготовка к сочинению и орфография.",
            18,
            3,
        )
    )
    messages.append(
        _msg(
            "chat_anna_olga",
            u[KEY_RUSSIAN_TUTOR],
            "Отлично, начнём с сочинения на следующем занятии.",
            18,
            2,
            False,
        )
    )

    # ── Anna ↔ Tatiana ────────────────────────────────────────
    messages.append(
        _msg(
            "chat_anna_tatiana",
            u[KEY_STUDENT_TATIANA],
            "Анна Сергеевна, добрый день! Готовлюсь к ЕГЭ по русскому.",
            15,
            6,
        )
    )
    messages.append(
        _msg(
            "chat_anna_tatiana",
            u[KEY_RUSSIAN_TUTOR],
            "Здравствуйте, Татьяна! Отлично, у меня есть много материалов.",
            15,
            5,
        )
    )
    messages.append(
        _msg(
            "chat_anna_tatiana",
            u[KEY_STUDENT_TATIANA],
            "Спасибо! Когда сможем провести пробный тест?",
            15,
            4,
            False,
        )
    )

    # ── Anna ↔ Dmitry ─────────────────────────────────────────
    messages.append(
        _msg(
            "chat_anna_dmitry",
            u[KEY_SUD_STUDENT],
            "Анна Сергеевна, нужно повысить грамотность для экзамена.",
            14,
            5,
        )
    )
    messages.append(
        _msg(
            "chat_anna_dmitry",
            u[KEY_RUSSIAN_TUTOR],
            "Дмитрий, добрый день! Проработаем все сложные темы.",
            14,
            4,
        )
    )
    messages.append(
        _msg(
            "chat_anna_dmitry",
            u[KEY_SUD_STUDENT],
            "Больше всего беспокоят знаки препинания.",
            14,
            3,
        )
    )
    messages.append(
        _msg(
            "chat_anna_dmitry",
            u[KEY_RUSSIAN_TUTOR],
            "Пунктуация — не проблема. Разберём на занятиях.",
            14,
            2,
        )
    )
    messages.append(
        _msg(
            "chat_anna_dmitry",
            u[KEY_SUD_STUDENT],
            "Договорились, спасибо!",
            14,
            1,
            False,
        )
    )

    # ── Anna ↔ Alexey (New1) ──────────────────────────────────
    messages.append(
        _msg(
            "chat_anna_new1",
            u[KEY_STUDENT_NEW1],
            "Здравствуйте! Ищу репетитора по русскому языку.",
            10,
            4,
        )
    )
    messages.append(
        _msg(
            "chat_anna_new1",
            u[KEY_RUSSIAN_TUTOR],
            "Здравствуйте, Алексей! Расскажите о ваших целях.",
            10,
            3,
        )
    )
    messages.append(
        _msg(
            "chat_anna_new1",
            u[KEY_STUDENT_NEW1],
            "Нужна помощь с подготовкой к ЕГЭ.",
            10,
            2,
            False,
        )
    )

    # ── Anna ↔ Maria (New2) ───────────────────────────────────
    messages.append(
        _msg(
            "chat_anna_new2",
            u[KEY_STUDENT_NEW2],
            "Здравствуйте! Хочу улучшить успеваемость по русскому.",
            8,
            5,
        )
    )
    messages.append(
        _msg(
            "chat_anna_new2",
            u[KEY_RUSSIAN_TUTOR],
            "Мария, здравствуйте! Приходите на пробное занятие.",
            8,
            4,
        )
    )
    messages.append(
        _msg("chat_anna_new2", u[KEY_STUDENT_NEW2], "Спасибо! Буду.", 8, 3, False)
    )

    # ── Dmitry ↔ Ivan (Math #1) ───────────────────────────────
    messages.append(
        _msg(
            "chat_dmitry_math1",
            u[KEY_SUD_STUDENT],
            "Иван Иванович, нужно подтянуть математику к ЕГЭ.",
            12,
            6,
        )
    )
    messages.append(
        _msg(
            "chat_dmitry_math1",
            u[KEY_MATH_1],
            "Дмитрий, здравствуйте! Какие разделы самые сложные?",
            12,
            5,
        )
    )
    messages.append(
        _msg(
            "chat_dmitry_math1",
            u[KEY_SUD_STUDENT],
            "Стереометрия и задачи с параметрами.",
            12,
            4,
        )
    )
    messages.append(
        _msg(
            "chat_dmitry_math1",
            u[KEY_MATH_1],
            "Понял. Составим план подготовки на ближайший месяц.",
            12,
            3,
        )
    )
    messages.append(
        _msg(
            "chat_dmitry_math1", u[KEY_SUD_STUDENT], "Отлично, жду план!", 12, 2, False
        )
    )

    # ── Dmitry ↔ Elena (Chemistry) ────────────────────────────
    messages.append(
        _msg(
            "chat_dmitry_chemistry",
            u[KEY_SUD_STUDENT],
            "Елена Дмитриевна, нужна помощь с химией.",
            11,
            5,
        )
    )
    messages.append(
        _msg(
            "chat_dmitry_chemistry",
            u[KEY_CHEMISTRY_TUTOR],
            "Дмитрий, привет! С чего начнём?",
            11,
            4,
        )
    )
    messages.append(
        _msg(
            "chat_dmitry_chemistry",
            u[KEY_SUD_STUDENT],
            "С органической химии, пожалуй.",
            11,
            3,
            False,
        )
    )

    # ── Dmitry ↔ Physics ──────────────────────────────────────
    messages.append(
        _msg(
            "chat_dmitry_physics",
            u[KEY_SUD_STUDENT],
            "Здравствуйте! Хочу освоить физику с нуля.",
            9,
            5,
        )
    )
    messages.append(
        _msg(
            "chat_dmitry_physics",
            u[KEY_PHYSICS_TUTOR],
            "Приветствую! Начнём с механики, это база.",
            9,
            4,
        )
    )
    messages.append(
        _msg(
            "chat_dmitry_physics",
            u[KEY_SUD_STUDENT],
            "Договорились. Когда первое занятие?",
            9,
            3,
            False,
        )
    )

    # ── Dmitry ↔ English ─────────────────────────────────────
    messages.append(
        _msg(
            "chat_dmitry_english",
            u[KEY_SUD_STUDENT],
            "Hello! I'd like to improve my English.",
            7,
            6,
        )
    )
    messages.append(
        _msg(
            "chat_dmitry_english",
            u[KEY_ENGLISH_TUTOR],
            "Hi Dmitry! We'll focus on speaking and grammar.",
            7,
            5,
        )
    )
    messages.append(
        _msg(
            "chat_dmitry_english", u[KEY_SUD_STUDENT], "Great! When can we start?", 7, 4
        )
    )
    messages.append(
        _msg(
            "chat_dmitry_english",
            u[KEY_ENGLISH_TUTOR],
            "Let's have a trial lesson this week.",
            7,
            3,
            False,
        )
    )

    session.add_all(messages)

    # ═══════════════════════════════════════════════════════════
    # 4. Lessons
    # ═══════════════════════════════════════════════════════════
    lesson_ids: dict[str, uuid.UUID] = {}

    def _lesson(
        store_key,
        student,
        tutor,
        days_offset,
        dur_hours=2,
        status=LessonStatus.completed,
        has_link=True,
    ):
        uid = _uid("d300")
        lesson_ids[store_key] = uid
        return Lesson(
            id=uid,
            student_id=student,
            tutor_id=tutor,
            start_datetime=NOW + timedelta(days=days_offset, hours=10),
            end_datetime=NOW + timedelta(days=days_offset, hours=10 + dur_hours),
            status=status,
            meeting_link=f"https://meet.google.com/lesson/{store_key}"
            if has_link
            else None,
        )

    lessons = []

    # ── Scenario 1: Russian tutor + 5 students ──────────────
    for i, (key_prefix, student_key) in enumerate(
        [
            ("olga", KEY_STUDENT_OLGA),
            ("tatiana", KEY_STUDENT_TATIANA),
            ("dmitry", KEY_SUD_STUDENT),
            ("new1", KEY_STUDENT_NEW1),
            ("new2", KEY_STUDENT_NEW2),
        ]
    ):
        # Completed (past)
        lessons.append(
            _lesson(
                f"anna_{key_prefix}_c",
                u[student_key],
                u[KEY_RUSSIAN_TUTOR],
                -15 + i * 2,
            )
        )
        # Planned (future)
        lessons.append(
            _lesson(
                f"anna_{key_prefix}_p",
                u[student_key],
                u[KEY_RUSSIAN_TUTOR],
                5 + i * 3,
                status=LessonStatus.planned,
                has_link=False,
            )
        )

    # ── Scenario 2: sud + 4 other tutors ────────────────────
    for i, (key_prefix, tutor_key) in enumerate(
        [
            ("math1", KEY_MATH_1),
            ("chemistry", KEY_CHEMISTRY_TUTOR),
            ("physics", KEY_PHYSICS_TUTOR),
            ("english", KEY_ENGLISH_TUTOR),
        ]
    ):
        lessons.append(
            _lesson(
                f"dmitry_{key_prefix}_c",
                u[KEY_SUD_STUDENT],
                u[tutor_key],
                -12 + i * 2,
            )
        )
        lessons.append(
            _lesson(
                f"dmitry_{key_prefix}_p",
                u[KEY_SUD_STUDENT],
                u[tutor_key],
                7 + i * 4,
                status=LessonStatus.planned,
                has_link=False,
            )
        )

    # ── Scenario 3: review lessons for math tutors #2-#5 ─────
    review_lessons = [
        ("math2_olga_review", u[KEY_STUDENT_OLGA], u[KEY_MATH_2]),
        ("math3_tatiana_review", u[KEY_STUDENT_TATIANA], u[KEY_MATH_3]),
        ("math4_new1_review", u[KEY_STUDENT_NEW1], u[KEY_MATH_4]),
        ("math5_new2_review", u[KEY_STUDENT_NEW2], u[KEY_MATH_5]),
    ]
    for store_key, student, tutor in review_lessons:
        lessons.append(_lesson(store_key, student, tutor, -22))

    session.add_all(lessons)

    # ═══════════════════════════════════════════════════════════
    # 5. Test Library  (unchanged, keep minimal)
    # ═══════════════════════════════════════════════════════════
    test_items = [
        TestLibrary(
            id=TEST_LIB_1_ID,
            subject_id=SUBJ_MATH,
            topic="Алгебра — уравнения и неравенства",
            questions_json={
                "questions": [
                    {
                        "id": 1,
                        "text": "Решите уравнение: x² - 5x + 6 = 0",
                        "options": [
                            "x = 2, x = 3",
                            "x = -2, x = -3",
                            "x = 1, x = 6",
                            "x = -1, x = -6",
                        ],
                        "correct": 0,
                    },
                    {
                        "id": 2,
                        "text": "Решите неравенство: 2x - 4 > 0",
                        "options": ["x > 2", "x < 2", "x > -2", "x > 0"],
                        "correct": 0,
                    },
                ],
            },
        ),
        TestLibrary(
            id=TEST_LIB_2_ID,
            subject_id=SUBJ_RUSSIAN,
            topic="Орфография — правописание приставок",
            questions_json={
                "questions": [
                    {
                        "id": 1,
                        "text": "В каком слове пишется приставка ПРЕ-?",
                        "options": [
                            "Пр...вратник",
                            "Пр...бежать",
                            "Пр...школьный",
                            "Пр...открыть",
                        ],
                        "correct": 0,
                    },
                ],
            },
        ),
    ]
    session.add_all(test_items)
    await session.flush()

    # ═══════════════════════════════════════════════════════════
    # 6. Reviews — 5 math tutors × 1 review each
    # ═══════════════════════════════════════════════════════════
    reviews = [
        # Math #1 (Ivan) ← Dmitry (uses dmitry_math1_c lesson)
        Review(
            id=_uid("c100"),
            student_id=u[KEY_SUD_STUDENT],
            tutor_id=u[KEY_MATH_1],
            lesson_id=lesson_ids["dmitry_math1_c"],
            communication_score=5,
            text="Иван Иванович — отличный преподаватель! "
            "Объясняет сложные темы простым языком. "
            "Готовлюсь к ЕГЭ и уже вижу прогресс.",
        ),
        # Math #2 (Alex) ← Olga
        Review(
            id=_uid("c100"),
            student_id=u[KEY_STUDENT_OLGA],
            tutor_id=u[KEY_MATH_2],
            lesson_id=lesson_ids["math2_olga_review"],
            communication_score=4,
            text="Алексей Петрович строгий, но справедливый. "
            "Требует много, но результат того стоит. Рекомендую!",
        ),
        # Math #3 (Zaitsev) ← Tatiana
        Review(
            id=_uid("c100"),
            student_id=u[KEY_STUDENT_TATIANA],
            tutor_id=u[KEY_MATH_3],
            lesson_id=lesson_ids["math3_tatiana_review"],
            communication_score=5,
            text="Дмитрий — молодой специалист, но очень старательный. "
            "Занятия проходят интересно и современно. Цена приятная.",
        ),
        # Math #4 (Sokolova) ← New1
        Review(
            id=_uid("c100"),
            student_id=u[KEY_STUDENT_NEW1],
            tutor_id=u[KEY_MATH_4],
            lesson_id=lesson_ids["math4_new1_review"],
            communication_score=4,
            text="Ольга Владимировна хорошо объясняет, но требует "
            "строгого выполнения домашних заданий. "
            "Подготовка к ЕГЭ на высшем уровне.",
        ),
        # Math #5 (Morozov) ← New2
        Review(
            id=_uid("c100"),
            student_id=u[KEY_STUDENT_NEW2],
            tutor_id=u[KEY_MATH_5],
            lesson_id=lesson_ids["math5_new2_review"],
            communication_score=5,
            text="Сергей Николаевич — профессионал высочайшего уровня. "
            "15 лет опыта чувствуются. "
            "Дорого, но качество обучения того стоит!",
        ),
    ]
    session.add_all(reviews)
