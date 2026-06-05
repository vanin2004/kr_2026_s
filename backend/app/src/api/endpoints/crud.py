"""Generic CRUD endpoints replacing PostgREST.

Provides RESTful endpoints for all database tables with filtering, sorting,
and pagination support.
"""

import uuid
from typing import Type

from db.session import get_db
from fastapi import APIRouter, Depends, HTTPException, Query, status
from models.base import Base as BaseModelClass
from models.tables import (
    Application,
    Chat,
    DeviceToken,
    Lesson,
    Message,
    Review,
    Schedule,
    StudentPreferredTag,
    StudentProfile,
    StudentResult,
    Subject,
    Tag,
    TestLibrary,
    TutorCertification,
    TutorProfile,
    TutorTag,
    User,
)
from schemas.api import (
    ApplicationCreate,
    ApplicationRead,
    ApplicationUpdate,
    ChatRead,
    DeviceTokenCreate,
    DeviceTokenRead,
    LessonCreate,
    LessonRead,
    LessonUpdate,
    MessageCreate,
    MessageRead,
    MessageUpdate,
    ReviewCreate,
    ReviewRead,
    ReviewUpdate,
    ScheduleCreate,
    ScheduleRead,
    ScheduleUpdate,
    StudentPreferredTagCreate,
    StudentPreferredTagRead,
    StudentProfileCreate,
    StudentProfileRead,
    StudentProfileUpdate,
    StudentResultCreate,
    StudentResultRead,
    StudentResultUpdate,
    SubjectCreate,
    SubjectRead,
    SubjectUpdate,
    TagCreate,
    TagRead,
    TagUpdate,
    TestLibraryCreate,
    TestLibraryRead,
    TestLibraryUpdate,
    TutorCertificationCreate,
    TutorCertificationRead,
    TutorCertificationUpdate,
    TutorProfileCreate,
    TutorProfileRead,
    TutorProfileUpdate,
    TutorTagCreate,
    TutorTagRead,
    UserRead,
)
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

# ─── Helper: filter by pk_field=eq.value ────────────────────────
# For simplicity, we support a limited set of filters:
#   ?field=eq.value  → WHERE field = value
#   ?field=in.1,2,3  → WHERE field IN (...)
# For complete PostgREST-like functionality, a more sophisticated
# parser would be needed. Our approach covers the main cases used
# in the mobile app.

FILTER_SEPARATORS = {
    "eq.": lambda col, val: col == val,
    "neq.": lambda col, val: col != val,
    "gt.": lambda col, val: col > val,
    "gte.": lambda col, val: col >= val,
    "lt.": lambda col, val: col < val,
    "lte.": lambda col, val: col <= val,
}


def _apply_filters(stmt, model: Type[BaseModelClass], query_params: dict[str, str]):
    """Apply PostgREST-style filters to a select statement."""
    for field_name, filter_str in query_params.items():
        if not hasattr(model, field_name):
            continue
        column = getattr(model, field_name)
        for prefix, comparator in FILTER_SEPARATORS.items():
            if filter_str.startswith(prefix):
                value = filter_str[len(prefix) :]
                # Try to parse value
                try:
                    value = uuid.UUID(value)
                except (ValueError, AttributeError):
                    try:
                        value = int(value)
                    except ValueError:
                        pass
                stmt = stmt.where(comparator(column, value))
                break
            elif filter_str.startswith("in."):
                values_str = filter_str[3:]
                values = []
                for v in values_str.split(","):
                    try:
                        values.append(uuid.UUID(v))
                    except (ValueError, AttributeError):
                        try:
                            values.append(int(v))
                        except ValueError:
                            values.append(v)
                stmt = stmt.where(column.in_(values))
                break
    return stmt


# ─── Users ──────────────────────────────────────────────────────
@router.get("/users", response_model=list[UserRead], tags=["users"])
async def list_users(
    db: AsyncSession = Depends(get_db),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    stmt = select(User).offset(offset).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/users/{user_id}", response_model=UserRead, tags=["users"])
async def get_user(user_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.delete(
    "/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["users"]
)
async def delete_user(user_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await db.delete(user)
    await db.flush()


# ─── Subjects (UUID PK) ─────────────────────────────────────────
@router.get("/subjects", response_model=list[SubjectRead], tags=["subjects"])
async def list_subjects(
    db: AsyncSession = Depends(get_db),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    stmt = select(Subject).offset(offset).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/subjects/{subject_id}", response_model=SubjectRead, tags=["subjects"])
async def get_subject(subject_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    stmt = select(Subject).where(Subject.id == subject_id)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Subject not found")
    return item


@router.post(
    "/subjects",
    response_model=SubjectRead,
    status_code=status.HTTP_201_CREATED,
    tags=["subjects"],
)
async def create_subject(data: SubjectCreate, db: AsyncSession = Depends(get_db)):
    item = Subject(**data.model_dump())
    db.add(item)
    await db.flush()
    await db.refresh(item)
    return item


@router.patch("/subjects/{subject_id}", response_model=SubjectRead, tags=["subjects"])
async def update_subject(
    subject_id: uuid.UUID,
    data: SubjectUpdate,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Subject).where(Subject.id == subject_id)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Subject not found")

    update_data = data.model_dump(exclude_unset=True)
    if update_data:
        await db.execute(
            update(Subject).where(Subject.id == subject_id).values(**update_data)
        )
        await db.flush()
        await db.refresh(item)
    return item


@router.delete(
    "/subjects/{subject_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["subjects"],
)
async def delete_subject(subject_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    stmt = select(Subject).where(Subject.id == subject_id)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Subject not found")
    await db.delete(item)
    await db.flush()


# ─── Tags (UUID PK) ─────────────────────────────────────────────
@router.get("/tags", response_model=list[TagRead], tags=["tags"])
async def list_tags(
    db: AsyncSession = Depends(get_db),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    stmt = select(Tag).offset(offset).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/tags/{tag_id}", response_model=TagRead, tags=["tags"])
async def get_tag(tag_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    stmt = select(Tag).where(Tag.id == tag_id)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Tag not found")
    return item


@router.post(
    "/tags",
    response_model=TagRead,
    status_code=status.HTTP_201_CREATED,
    tags=["tags"],
)
async def create_tag(data: TagCreate, db: AsyncSession = Depends(get_db)):
    item = Tag(**data.model_dump())
    db.add(item)
    await db.flush()
    await db.refresh(item)
    return item


@router.patch("/tags/{tag_id}", response_model=TagRead, tags=["tags"])
async def update_tag(
    tag_id: uuid.UUID,
    data: TagUpdate,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Tag).where(Tag.id == tag_id)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Tag not found")

    update_data = data.model_dump(exclude_unset=True)
    if update_data:
        await db.execute(update(Tag).where(Tag.id == tag_id).values(**update_data))
        await db.flush()
        await db.refresh(item)
    return item


@router.delete(
    "/tags/{tag_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["tags"],
)
async def delete_tag(tag_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    stmt = select(Tag).where(Tag.id == tag_id)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Tag not found")
    await db.delete(item)
    await db.flush()


# ─── Tutor Profiles ─────────────────────────────────────────────
@router.get(
    "/tutor_profiles", response_model=list[TutorProfileRead], tags=["tutor_profiles"]
)
async def list_tutor_profiles(
    db: AsyncSession = Depends(get_db),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    subject_id: uuid.UUID | None = Query(None),
    hourly_rate_lte: int | None = Query(None),
):
    stmt = select(TutorProfile).offset(offset).limit(limit)
    if subject_id is not None:
        stmt = stmt.where(TutorProfile.subject_id == subject_id)
    if hourly_rate_lte is not None:
        stmt = stmt.where(TutorProfile.hourly_rate <= hourly_rate_lte)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get(
    "/tutor_profiles/{user_id}",
    response_model=TutorProfileRead,
    tags=["tutor_profiles"],
)
async def get_tutor_profile(user_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    stmt = select(TutorProfile).where(TutorProfile.user_id == user_id)
    result = await db.execute(stmt)
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Tutor profile not found")
    return profile


@router.post(
    "/tutor_profiles",
    response_model=TutorProfileRead,
    status_code=status.HTTP_201_CREATED,
    tags=["tutor_profiles"],
)
async def create_tutor_profile(
    data: TutorProfileCreate, db: AsyncSession = Depends(get_db)
):
    profile = TutorProfile(**data.model_dump())
    db.add(profile)
    await db.flush()
    await db.refresh(profile)
    return profile


@router.patch(
    "/tutor_profiles/{user_id}",
    response_model=TutorProfileRead,
    tags=["tutor_profiles"],
)
async def update_tutor_profile(
    user_id: uuid.UUID,
    data: TutorProfileUpdate,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(TutorProfile).where(TutorProfile.user_id == user_id)
    result = await db.execute(stmt)
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Tutor profile not found")

    update_data = data.model_dump(exclude_unset=True)
    if update_data:
        await db.execute(
            update(TutorProfile)
            .where(TutorProfile.user_id == user_id)
            .values(**update_data)
        )
        await db.flush()
        await db.refresh(profile)
    return profile


@router.delete(
    "/tutor_profiles/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["tutor_profiles"],
)
async def delete_tutor_profile(user_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    stmt = select(TutorProfile).where(TutorProfile.user_id == user_id)
    result = await db.execute(stmt)
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Tutor profile not found")
    await db.delete(profile)
    await db.flush()


# ─── Student Profiles ───────────────────────────────────────────
@router.get(
    "/student_profiles",
    response_model=list[StudentProfileRead],
    tags=["student_profiles"],
)
async def list_student_profiles(
    db: AsyncSession = Depends(get_db),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    stmt = select(StudentProfile).offset(offset).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get(
    "/student_profiles/{user_id}",
    response_model=StudentProfileRead,
    tags=["student_profiles"],
)
async def get_student_profile(user_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    stmt = select(StudentProfile).where(StudentProfile.user_id == user_id)
    result = await db.execute(stmt)
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Student profile not found")
    return profile


@router.post(
    "/student_profiles",
    response_model=StudentProfileRead,
    status_code=status.HTTP_201_CREATED,
    tags=["student_profiles"],
)
async def create_student_profile(
    data: StudentProfileCreate, db: AsyncSession = Depends(get_db)
):
    profile_data = data.model_dump()
    if profile_data.get("search_weights") is None:
        profile_data["search_weights"] = {
            "k1_effectiveness": 0.30,
            "k2_communication": 0.15,
            "k3_expertise": 0.20,
            "k4_responsiveness": 0.15,
            "k5_tags": 0.20,
        }
    profile = StudentProfile(**profile_data)
    db.add(profile)
    await db.flush()
    await db.refresh(profile)
    return profile


@router.patch(
    "/student_profiles/{user_id}",
    response_model=StudentProfileRead,
    tags=["student_profiles"],
)
async def update_student_profile(
    user_id: uuid.UUID,
    data: StudentProfileUpdate,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(StudentProfile).where(StudentProfile.user_id == user_id)
    result = await db.execute(stmt)
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Student profile not found")

    update_data = data.model_dump(exclude_unset=True)
    if update_data:
        await db.execute(
            update(StudentProfile)
            .where(StudentProfile.user_id == user_id)
            .values(**update_data)
        )
        await db.flush()
        await db.refresh(profile)
    return profile


@router.delete(
    "/student_profiles/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["student_profiles"],
)
async def delete_student_profile(
    user_id: uuid.UUID, db: AsyncSession = Depends(get_db)
):
    stmt = select(StudentProfile).where(StudentProfile.user_id == user_id)
    result = await db.execute(stmt)
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Student profile not found")
    await db.delete(profile)
    await db.flush()


# ─── Tutor Tags (composite PK) ──────────────────────────────────


@router.get("/tutor_tags", response_model=list[TutorTagRead], tags=["tutor_tags"])
async def list_tutor_tags(
    db: AsyncSession = Depends(get_db),
    tutor_id: uuid.UUID | None = Query(None),
    tag_id: uuid.UUID | None = Query(None),
):
    stmt = select(TutorTag)
    if tutor_id is not None:
        stmt = stmt.where(TutorTag.tutor_id == tutor_id)
    if tag_id is not None:
        stmt = stmt.where(TutorTag.tag_id == tag_id)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post(
    "/tutor_tags",
    response_model=TutorTagRead,
    status_code=status.HTTP_201_CREATED,
    tags=["tutor_tags"],
)
async def create_tutor_tag(data: TutorTagCreate, db: AsyncSession = Depends(get_db)):
    tag = TutorTag(**data.model_dump())
    db.add(tag)
    await db.flush()
    await db.refresh(tag)
    return tag


@router.delete(
    "/tutor_tags",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["tutor_tags"],
)
async def delete_tutor_tag(
    tutor_id: uuid.UUID = Query(...),
    tag_id: uuid.UUID = Query(...),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(TutorTag).where(
        TutorTag.tutor_id == tutor_id, TutorTag.tag_id == tag_id
    )
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Tutor tag not found")
    await db.delete(item)
    await db.flush()


# ─── Student Preferred Tags (composite PK) ──────────────────────
@router.get(
    "/student_preferred_tags",
    response_model=list[StudentPreferredTagRead],
    tags=["student_preferred_tags"],
)
async def list_student_preferred_tags(
    db: AsyncSession = Depends(get_db),
    student_id: uuid.UUID | None = Query(None),
):
    stmt = select(StudentPreferredTag)
    if student_id is not None:
        stmt = stmt.where(StudentPreferredTag.student_id == student_id)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post(
    "/student_preferred_tags",
    response_model=StudentPreferredTagRead,
    status_code=status.HTTP_201_CREATED,
    tags=["student_preferred_tags"],
)
async def create_student_preferred_tag(
    data: StudentPreferredTagCreate, db: AsyncSession = Depends(get_db)
):
    tag = StudentPreferredTag(**data.model_dump())
    db.add(tag)
    await db.flush()
    await db.refresh(tag)
    return tag


@router.delete(
    "/student_preferred_tags",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["student_preferred_tags"],
)
async def delete_student_preferred_tag(
    student_id: uuid.UUID = Query(...),
    tag_id: uuid.UUID = Query(...),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(StudentPreferredTag).where(
        StudentPreferredTag.student_id == student_id,
        StudentPreferredTag.tag_id == tag_id,
    )
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Student preferred tag not found")
    await db.delete(item)
    await db.flush()


# ─── Tutor Certifications ───────────────────────────────────────
@router.get(
    "/tutor_certifications",
    response_model=list[TutorCertificationRead],
    tags=["tutor_certifications"],
)
async def list_tutor_certifications(
    db: AsyncSession = Depends(get_db),
    tutor_id: uuid.UUID | None = Query(None),
):
    stmt = select(TutorCertification)
    if tutor_id is not None:
        stmt = stmt.where(TutorCertification.tutor_id == tutor_id)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post(
    "/tutor_certifications",
    response_model=TutorCertificationRead,
    status_code=status.HTTP_201_CREATED,
    tags=["tutor_certifications"],
)
async def create_tutor_certification(
    data: TutorCertificationCreate, db: AsyncSession = Depends(get_db)
):
    cert = TutorCertification(**data.model_dump())
    db.add(cert)
    await db.flush()
    await db.refresh(cert)
    return cert


@router.get(
    "/tutor_certifications/{cert_id}",
    response_model=TutorCertificationRead,
    tags=["tutor_certifications"],
)
async def get_tutor_certification(cert_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(TutorCertification).where(TutorCertification.id == cert_id)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Tutor certification not found")
    return item


@router.patch(
    "/tutor_certifications/{cert_id}",
    response_model=TutorCertificationRead,
    tags=["tutor_certifications"],
)
async def update_tutor_certification(
    cert_id: int,
    data: TutorCertificationUpdate,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(TutorCertification).where(TutorCertification.id == cert_id)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Tutor certification not found")

    update_data = data.model_dump(exclude_unset=True)
    if update_data:
        await db.execute(
            update(TutorCertification)
            .where(TutorCertification.id == cert_id)
            .values(**update_data)
        )
        await db.flush()
        await db.refresh(item)
    return item


@router.delete(
    "/tutor_certifications/{cert_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["tutor_certifications"],
)
async def delete_tutor_certification(cert_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(TutorCertification).where(TutorCertification.id == cert_id)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Tutor certification not found")
    await db.delete(item)
    await db.flush()


# ─── Schedules ──────────────────────────────────────────────────
@router.get("/schedules", response_model=list[ScheduleRead], tags=["schedules"])
async def list_schedules(
    db: AsyncSession = Depends(get_db),
    tutor_id: uuid.UUID | None = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    stmt = select(Schedule).offset(offset).limit(limit)
    if tutor_id is not None:
        stmt = stmt.where(Schedule.tutor_id == tutor_id)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get(
    "/schedules/{schedule_id}",
    response_model=ScheduleRead,
    tags=["schedules"],
)
async def get_schedule(schedule_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(Schedule).where(Schedule.id == schedule_id)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return item


@router.post(
    "/schedules",
    response_model=ScheduleRead,
    status_code=status.HTTP_201_CREATED,
    tags=["schedules"],
)
async def create_schedule(data: ScheduleCreate, db: AsyncSession = Depends(get_db)):
    item = Schedule(**data.model_dump())
    db.add(item)
    await db.flush()
    await db.refresh(item)
    return item


@router.patch(
    "/schedules/{schedule_id}",
    response_model=ScheduleRead,
    tags=["schedules"],
)
async def update_schedule(
    schedule_id: int,
    data: ScheduleUpdate,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Schedule).where(Schedule.id == schedule_id)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Schedule not found")

    update_data = data.model_dump(exclude_unset=True)
    if update_data:
        await db.execute(
            update(Schedule).where(Schedule.id == schedule_id).values(**update_data)
        )
        await db.flush()
        await db.refresh(item)
    return item


@router.delete(
    "/schedules/{schedule_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["schedules"],
)
async def delete_schedule(schedule_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(Schedule).where(Schedule.id == schedule_id)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Schedule not found")
    await db.delete(item)
    await db.flush()


# ─── Lessons ────────────────────────────────────────────────────
@router.get("/lessons", response_model=list[LessonRead], tags=["lessons"])
async def list_lessons(
    db: AsyncSession = Depends(get_db),
    student_id: uuid.UUID | None = Query(None),
    tutor_id: uuid.UUID | None = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    stmt = select(Lesson).offset(offset).limit(limit)
    if student_id is not None:
        stmt = stmt.where(Lesson.student_id == student_id)
    if tutor_id is not None:
        stmt = stmt.where(Lesson.tutor_id == tutor_id)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get(
    "/lessons/{lesson_id}",
    response_model=LessonRead,
    tags=["lessons"],
)
async def get_lesson(lesson_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    stmt = select(Lesson).where(Lesson.id == lesson_id)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return item


@router.post(
    "/lessons",
    response_model=LessonRead,
    status_code=status.HTTP_201_CREATED,
    tags=["lessons"],
)
async def create_lesson(data: LessonCreate, db: AsyncSession = Depends(get_db)):
    item = Lesson(**data.model_dump())
    db.add(item)
    await db.flush()
    await db.refresh(item)
    return item


@router.patch(
    "/lessons/{lesson_id}",
    response_model=LessonRead,
    tags=["lessons"],
)
async def update_lesson(
    lesson_id: uuid.UUID,
    data: LessonUpdate,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Lesson).where(Lesson.id == lesson_id)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Lesson not found")

    update_data = data.model_dump(exclude_unset=True)
    if update_data:
        await db.execute(
            update(Lesson).where(Lesson.id == lesson_id).values(**update_data)
        )
        await db.flush()
        await db.refresh(item)
    return item


# ─── Applications ───────────────────────────────────────────────
@router.get(
    "/applications",
    response_model=list[ApplicationRead],
    tags=["applications"],
)
async def list_applications(
    db: AsyncSession = Depends(get_db),
    student_id: uuid.UUID | None = Query(None),
    tutor_id: uuid.UUID | None = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    stmt = select(Application).offset(offset).limit(limit)
    if student_id is not None:
        stmt = stmt.where(Application.student_id == student_id)
    if tutor_id is not None:
        stmt = stmt.where(Application.tutor_id == tutor_id)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post(
    "/applications",
    response_model=ApplicationRead,
    status_code=status.HTTP_201_CREATED,
    tags=["applications"],
)
async def create_application(
    data: ApplicationCreate, db: AsyncSession = Depends(get_db)
):
    # Проверяем, что student и tutor существуют
    student = await db.execute(select(User).where(User.id == data.student_id))
    if not student.scalar_one_or_none():
        raise HTTPException(
            status_code=404,
            detail=f"User (student) with id {data.student_id} not found",
        )

    tutor = await db.execute(select(User).where(User.id == data.tutor_id))
    if not tutor.scalar_one_or_none():
        raise HTTPException(
            status_code=404,
            detail=f"User (tutor) with id {data.tutor_id} not found",
        )

    item = Application(**data.model_dump())
    db.add(item)
    try:
        await db.flush()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Application already exists for this student-tutor pair",
        )
    await db.refresh(item)
    return item


@router.patch(
    "/applications/{application_id}",
    response_model=ApplicationRead,
    tags=["applications"],
)
async def update_application(
    application_id: uuid.UUID,
    data: ApplicationUpdate,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Application).where(Application.id == application_id)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Application not found")

    update_data = data.model_dump(exclude_unset=True)
    if update_data:
        from datetime import datetime, timezone

        now = datetime.now(timezone.utc)
        update_values = {}
        if "status" in update_data:
            update_values["responded_at"] = now

        await db.execute(
            update(Application)
            .where(Application.id == application_id)
            .values(**update_data, **update_values)
        )

        if "status" in update_data and update_data["status"] == "accepted":
            # Create chat for accepted application
            chat = Chat(application_id=application_id)
            db.add(chat)

        await db.flush()
        await db.refresh(item)
    return item


@router.delete(
    "/lessons/{lesson_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["lessons"],
)
async def delete_lesson(lesson_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    stmt = select(Lesson).where(Lesson.id == lesson_id)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Lesson not found")
    await db.delete(item)
    await db.flush()


@router.get(
    "/applications/{application_id}",
    response_model=ApplicationRead,
    tags=["applications"],
)
async def get_application(
    application_id: uuid.UUID, db: AsyncSession = Depends(get_db)
):
    stmt = select(Application).where(Application.id == application_id)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Application not found")
    return item


@router.delete(
    "/applications/{application_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["applications"],
)
async def delete_application(
    application_id: uuid.UUID, db: AsyncSession = Depends(get_db)
):
    stmt = select(Application).where(Application.id == application_id)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Application not found")
    await db.delete(item)
    await db.flush()


# ─── Chats ──────────────────────────────────────────────────────
@router.get("/chats", response_model=list[ChatRead], tags=["chats"])
async def list_chats(
    db: AsyncSession = Depends(get_db),
    application_id: uuid.UUID | None = Query(None),
):
    stmt = select(Chat)
    if application_id is not None:
        stmt = stmt.where(Chat.application_id == application_id)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get(
    "/chats/{chat_id}",
    response_model=ChatRead,
    tags=["chats"],
)
async def get_chat(chat_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    stmt = select(Chat).where(Chat.id == chat_id)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Chat not found")
    return item


# ─── Messages ───────────────────────────────────────────────────
@router.get("/messages", response_model=list[MessageRead], tags=["messages"])
async def list_messages(
    db: AsyncSession = Depends(get_db),
    chat_id: uuid.UUID | None = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    stmt = select(Message).offset(offset).limit(limit)
    if chat_id is not None:
        stmt = stmt.where(Message.chat_id == chat_id)
    stmt = stmt.order_by(Message.created_at)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post(
    "/messages",
    response_model=MessageRead,
    status_code=status.HTTP_201_CREATED,
    tags=["messages"],
)
async def create_message(data: MessageCreate, db: AsyncSession = Depends(get_db)):
    item = Message(**data.model_dump())
    db.add(item)
    await db.flush()
    await db.refresh(item)
    return item


@router.patch(
    "/messages/{message_id}",
    response_model=MessageRead,
    tags=["messages"],
)
async def update_message(
    message_id: uuid.UUID,
    data: MessageUpdate,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Message).where(Message.id == message_id)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Message not found")

    update_data = data.model_dump(exclude_unset=True)
    if update_data:
        await db.execute(
            update(Message).where(Message.id == message_id).values(**update_data)
        )
        await db.flush()
        await db.refresh(item)
    return item


@router.get(
    "/messages/{message_id}",
    response_model=MessageRead,
    tags=["messages"],
)
async def get_message(message_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    stmt = select(Message).where(Message.id == message_id)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Message not found")
    return item


@router.delete(
    "/messages/{message_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["messages"],
)
async def delete_message(message_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    stmt = select(Message).where(Message.id == message_id)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Message not found")
    await db.delete(item)
    await db.flush()


# ─── Test Library ───────────────────────────────────────────────
@router.get(
    "/test_library",
    response_model=list[TestLibraryRead],
    tags=["test_library"],
)
async def list_test_library(
    db: AsyncSession = Depends(get_db),
    subject_id: uuid.UUID | None = Query(None),
):
    stmt = select(TestLibrary)
    if subject_id is not None:
        stmt = stmt.where(TestLibrary.subject_id == subject_id)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post(
    "/test_library",
    response_model=TestLibraryRead,
    status_code=status.HTTP_201_CREATED,
    tags=["test_library"],
)
async def create_test_library(
    data: TestLibraryCreate, db: AsyncSession = Depends(get_db)
):
    item = TestLibrary(**data.model_dump())
    db.add(item)
    await db.flush()
    await db.refresh(item)
    return item


@router.get(
    "/test_library/{test_id}",
    response_model=TestLibraryRead,
    tags=["test_library"],
)
async def get_test_library(test_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    stmt = select(TestLibrary).where(TestLibrary.id == test_id)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Test library entry not found")
    return item


@router.patch(
    "/test_library/{test_id}",
    response_model=TestLibraryRead,
    tags=["test_library"],
)
async def update_test_library(
    test_id: uuid.UUID,
    data: TestLibraryUpdate,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(TestLibrary).where(TestLibrary.id == test_id)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Test library entry not found")

    update_data = data.model_dump(exclude_unset=True)
    if update_data:
        await db.execute(
            update(TestLibrary).where(TestLibrary.id == test_id).values(**update_data)
        )
        await db.flush()
        await db.refresh(item)
    return item


@router.delete(
    "/test_library/{test_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["test_library"],
)
async def delete_test_library(test_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    stmt = select(TestLibrary).where(TestLibrary.id == test_id)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Test library entry not found")
    await db.delete(item)
    await db.flush()


# ─── Student Results ────────────────────────────────────────────
@router.get(
    "/student_results",
    response_model=list[StudentResultRead],
    tags=["student_results"],
)
async def list_student_results(
    db: AsyncSession = Depends(get_db),
    student_id: uuid.UUID | None = Query(None),
    tutor_id: uuid.UUID | None = Query(None),
):
    stmt = select(StudentResult)
    if student_id is not None:
        stmt = stmt.where(StudentResult.student_id == student_id)
    if tutor_id is not None:
        stmt = stmt.where(StudentResult.tutor_id == tutor_id)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post(
    "/student_results",
    response_model=StudentResultRead,
    status_code=status.HTTP_201_CREATED,
    tags=["student_results"],
)
async def create_student_result(
    data: StudentResultCreate, db: AsyncSession = Depends(get_db)
):
    item = StudentResult(**data.model_dump())
    db.add(item)
    await db.flush()
    await db.refresh(item)
    return item


@router.patch(
    "/student_results/{result_id}",
    response_model=StudentResultRead,
    tags=["student_results"],
)
async def update_student_result(
    result_id: uuid.UUID,
    data: StudentResultUpdate,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(StudentResult).where(StudentResult.id == result_id)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Student result not found")

    update_data = data.model_dump(exclude_unset=True)
    if update_data:
        await db.execute(
            update(StudentResult)
            .where(StudentResult.id == result_id)
            .values(**update_data)
        )
        await db.flush()
        await db.refresh(item)
    return item


@router.get(
    "/student_results/{result_id}",
    response_model=StudentResultRead,
    tags=["student_results"],
)
async def get_student_result(result_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    stmt = select(StudentResult).where(StudentResult.id == result_id)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Student result not found")
    return item


@router.delete(
    "/student_results/{result_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["student_results"],
)
async def delete_student_result(
    result_id: uuid.UUID, db: AsyncSession = Depends(get_db)
):
    stmt = select(StudentResult).where(StudentResult.id == result_id)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Student result not found")
    await db.delete(item)
    await db.flush()


# ─── Reviews ────────────────────────────────────────────────────
@router.get("/reviews", response_model=list[ReviewRead], tags=["reviews"])
async def list_reviews(
    db: AsyncSession = Depends(get_db),
    tutor_id: uuid.UUID | None = Query(None),
    student_id: uuid.UUID | None = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    stmt = select(Review).offset(offset).limit(limit)
    if tutor_id is not None:
        stmt = stmt.where(Review.tutor_id == tutor_id)
    if student_id is not None:
        stmt = stmt.where(Review.student_id == student_id)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post(
    "/reviews",
    response_model=ReviewRead,
    status_code=status.HTTP_201_CREATED,
    tags=["reviews"],
)
async def create_review(data: ReviewCreate, db: AsyncSession = Depends(get_db)):
    item = Review(**data.model_dump())
    db.add(item)
    await db.flush()
    await db.refresh(item)
    return item


@router.get(
    "/reviews/{review_id}",
    response_model=ReviewRead,
    tags=["reviews"],
)
async def get_review(review_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    stmt = select(Review).where(Review.id == review_id)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Review not found")
    return item


@router.patch(
    "/reviews/{review_id}",
    response_model=ReviewRead,
    tags=["reviews"],
)
async def update_review(
    review_id: uuid.UUID,
    data: ReviewUpdate,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Review).where(Review.id == review_id)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Review not found")

    update_data = data.model_dump(exclude_unset=True)
    if update_data:
        await db.execute(
            update(Review).where(Review.id == review_id).values(**update_data)
        )
        await db.flush()
        await db.refresh(item)
    return item


@router.delete(
    "/reviews/{review_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["reviews"],
)
async def delete_review(review_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    stmt = select(Review).where(Review.id == review_id)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Review not found")
    await db.delete(item)
    await db.flush()


# ─── Device Tokens ──────────────────────────────────────────────
@router.get(
    "/device_tokens",
    response_model=list[DeviceTokenRead],
    tags=["device_tokens"],
)
async def list_device_tokens(
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID | None = Query(None),
):
    stmt = select(DeviceToken)
    if user_id is not None:
        stmt = stmt.where(DeviceToken.user_id == user_id)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post(
    "/device_tokens",
    response_model=DeviceTokenRead,
    status_code=status.HTTP_201_CREATED,
    tags=["device_tokens"],
)
async def create_device_token(
    data: DeviceTokenCreate, db: AsyncSession = Depends(get_db)
):
    item = DeviceToken(**data.model_dump())
    db.add(item)
    await db.flush()
    await db.refresh(item)
    return item


@router.delete(
    "/device_tokens/{token_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["device_tokens"],
)
async def delete_device_token(token_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(DeviceToken).where(DeviceToken.id == token_id)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Device token not found")
    await db.delete(item)
    await db.flush()


@router.get(
    "/device_tokens/{token_id}",
    response_model=DeviceTokenRead,
    tags=["device_tokens"],
)
async def get_device_token(token_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(DeviceToken).where(DeviceToken.id == token_id)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Device token not found")
    return item
