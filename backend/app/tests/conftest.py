"""
Shared fixtures for FastAPI tests.

Uses an in-memory SQLite database (aiosqlite) to test endpoints without
a real Postgres / Keycloak setup.
"""

import asyncio
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from db.session import get_db
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from models.base import Base
from models.enums import (
    ApplicationStatus,
    DevicePlatform,
    LessonStatus,
    ResultType,
    UserRole,
)
from models.tables import (
    Application,
    Chat,
    DeviceToken,
    Lesson,
    Message,
    Review,
    StudentPreferredTag,
    StudentProfile,
    StudentResult,
    Subject,
    Tag,
    TestLibrary,
    TutorCertification,
    TutorProfile,
    User,
)
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from src.main import app as real_app

# ---------------------------------------------------------------------------
# In-memory SQLite async engine – super fast, no external deps
# ---------------------------------------------------------------------------
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
)

TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture(scope="session")
def event_loop():
    """Create a single event loop for the whole test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    """Create all tables before each test and drop them after."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    """Override the FastAPI dependency to use the test database."""
    async with TestSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


@pytest_asyncio.fixture
async def app() -> FastAPI:
    """Return the FastAPI app with the test DB override."""
    real_app.dependency_overrides[get_db] = override_get_db
    return real_app


@pytest_asyncio.fixture
async def client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """Provide an async HTTPX client pointed at the test app."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# ---------------------------------------------------------------------------
# Helpers to seed test data
# ---------------------------------------------------------------------------
@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide a raw DB session for test data setup."""
    async with TestSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def seed_subjects(db_session: AsyncSession) -> list[Subject]:
    """Insert sample subjects."""
    subjects = [
        Subject(name="Mathematics"),
        Subject(name="Physics"),
        Subject(name="English"),
    ]
    for s in subjects:
        db_session.add(s)
    await db_session.flush()
    for s in subjects:
        await db_session.refresh(s)
    return subjects


@pytest_asyncio.fixture
async def seed_tags(db_session: AsyncSession) -> list[Tag]:
    """Insert sample tags."""
    tags = [
        Tag(name="exam-prep"),
        Tag(name="beginner"),
        Tag(name="advanced"),
    ]
    for t in tags:
        db_session.add(t)
    await db_session.flush()
    for t in tags:
        await db_session.refresh(t)
    return tags


@pytest_asyncio.fixture
async def seed_users(db_session: AsyncSession) -> dict[str, User]:
    """Insert a tutor and a student user."""
    import uuid

    tutor = User(
        id=uuid.uuid4(),
        email="tutor@example.com",
        role=UserRole.tutor,
    )
    student = User(
        id=uuid.uuid4(),
        email="student@example.com",
        role=UserRole.student,
    )
    db_session.add_all([tutor, student])
    await db_session.flush()
    for u in (tutor, student):
        await db_session.refresh(u)
    return {"tutor": tutor, "student": student}


@pytest_asyncio.fixture
async def seed_student_profile(
    db_session: AsyncSession,
    seed_users: dict[str, User],
) -> StudentProfile:
    """Insert a student profile linked to the student user."""
    profile = StudentProfile(
        user_id=seed_users["student"].id,
        full_name="Jane Student",
    )
    db_session.add(profile)
    await db_session.flush()
    await db_session.refresh(profile)
    return profile


@pytest_asyncio.fixture
async def seed_lesson(
    db_session: AsyncSession,
    seed_users: dict[str, User],
) -> Lesson:
    """Insert a sample lesson."""
    from datetime import datetime, timedelta, timezone

    now = datetime.now(timezone.utc)
    lesson = Lesson(
        student_id=seed_users["student"].id,
        tutor_id=seed_users["tutor"].id,
        start_datetime=now,
        end_datetime=now + timedelta(hours=1),
        status=LessonStatus.planned,
    )
    db_session.add(lesson)
    await db_session.flush()
    await db_session.refresh(lesson)
    return lesson


@pytest_asyncio.fixture
async def seed_application(
    db_session: AsyncSession,
    seed_users: dict[str, User],
) -> Application:
    """Insert a sample application."""
    app = Application(
        student_id=seed_users["student"].id,
        tutor_id=seed_users["tutor"].id,
        status=ApplicationStatus.pending,
    )
    db_session.add(app)
    await db_session.flush()
    await db_session.refresh(app)
    return app


@pytest_asyncio.fixture
async def seed_chat(
    db_session: AsyncSession,
    seed_application: Application,
) -> Chat:
    """Insert a chat linked to an application."""
    chat = Chat(application_id=seed_application.id)
    db_session.add(chat)
    await db_session.flush()
    await db_session.refresh(chat)
    return chat


@pytest_asyncio.fixture
async def seed_message(
    db_session: AsyncSession,
    seed_chat: Chat,
    seed_users: dict[str, User],
) -> Message:
    """Insert a sample message."""
    msg = Message(
        chat_id=seed_chat.id,
        sender_id=seed_users["tutor"].id,
        text="Hello, this is a test message!",
    )
    db_session.add(msg)
    await db_session.flush()
    await db_session.refresh(msg)
    return msg


@pytest_asyncio.fixture
async def seed_test_library(
    db_session: AsyncSession,
    seed_subjects: list[Subject],
) -> TestLibrary:
    """Insert a sample test in the library."""
    test = TestLibrary(
        subject_id=seed_subjects[0].id,
        topic="Algebra Basics",
        questions_json={"questions": [{"q": "2+2?", "a": "4"}]},
    )
    db_session.add(test)
    await db_session.flush()
    await db_session.refresh(test)
    return test


@pytest_asyncio.fixture
async def seed_student_result(
    db_session: AsyncSession,
    seed_users: dict[str, User],
    seed_test_library: TestLibrary,
) -> StudentResult:
    """Insert a sample student result."""
    from datetime import datetime, timezone

    result = StudentResult(
        student_id=seed_users["student"].id,
        tutor_id=seed_users["tutor"].id,
        test_id=seed_test_library.id,
        type=ResultType.initial_test,
        assigned_at=datetime.now(timezone.utc),
    )
    db_session.add(result)
    await db_session.flush()
    await db_session.refresh(result)
    return result


@pytest_asyncio.fixture
async def seed_review(
    db_session: AsyncSession,
    seed_users: dict[str, User],
    seed_lesson: Lesson,
) -> Review:
    """Insert a sample review."""
    review = Review(
        student_id=seed_users["student"].id,
        tutor_id=seed_users["tutor"].id,
        lesson_id=seed_lesson.id,
        communication_score=5,
        text="Great tutor!",
    )
    db_session.add(review)
    await db_session.flush()
    await db_session.refresh(review)
    return review


@pytest_asyncio.fixture
async def seed_device_token(
    db_session: AsyncSession,
    seed_users: dict[str, User],
) -> DeviceToken:
    """Insert a sample device token."""
    import uuid

    token = DeviceToken(
        user_id=seed_users["tutor"].id,
        token=f"fcm-token-{uuid.uuid4().hex}",
        platform=DevicePlatform.android,
    )
    db_session.add(token)
    await db_session.flush()
    await db_session.refresh(token)
    return token


@pytest_asyncio.fixture
async def seed_tutor_certification(
    db_session: AsyncSession,
    seed_users: dict[str, User],
) -> TutorCertification:
    """Insert a sample tutor certification."""
    cert = TutorCertification(
        tutor_id=seed_users["tutor"].id,
        title="Teaching Certificate",
        file_url="http://example.com/cert.pdf",
    )
    db_session.add(cert)
    await db_session.flush()
    await db_session.refresh(cert)
    return cert


@pytest_asyncio.fixture
async def seed_student_preferred_tag(
    db_session: AsyncSession,
    seed_users: dict[str, User],
    seed_tags: list[Tag],
) -> StudentPreferredTag:
    """Insert a sample student preferred tag."""
    spt = StudentPreferredTag(
        student_id=seed_users["student"].id,
        tag_id=seed_tags[0].id,
        is_required=True,
    )
    db_session.add(spt)
    await db_session.flush()
    await db_session.refresh(spt)
    return spt


@pytest_asyncio.fixture
async def seed_tutor_profile(
    db_session: AsyncSession,
    seed_users: dict[str, User],
    seed_subjects: list[Subject],
) -> TutorProfile:
    """Insert a tutor profile linked to the tutor user."""
    profile = TutorProfile(
        user_id=seed_users["tutor"].id,
        full_name="John Doe",
        subject_id=seed_subjects[0].id,
        hourly_rate=50,
        experience_years=5,
        is_verified=True,
    )
    db_session.add(profile)
    await db_session.flush()
    await db_session.refresh(profile)
    return profile
