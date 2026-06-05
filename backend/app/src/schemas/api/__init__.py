"""Pydantic v2 schemas for all CRUD endpoints — package.

Re-exports all schema classes from domain-specific submodules
for backward compatibility (from schemas.api import <Schema>).
"""

from schemas.api.applications import (
    ApplicationCreate,
    ApplicationRead,
    ApplicationUpdate,
)
from schemas.api.auth import RegisterRequest, RegisterResponse
from schemas.api.chats import ChatRead
from schemas.api.device_tokens import DeviceTokenCreate, DeviceTokenRead
from schemas.api.lessons import LessonCreate, LessonRead, LessonUpdate
from schemas.api.messages import MessageCreate, MessageRead, MessageUpdate
from schemas.api.reviews import ReviewCreate, ReviewRead, ReviewUpdate
from schemas.api.schedules import ScheduleCreate, ScheduleRead, ScheduleUpdate
from schemas.api.student_preferred_tags import (
    StudentPreferredTagCreate,
    StudentPreferredTagRead,
)
from schemas.api.student_profiles import (
    StudentProfileCreate,
    StudentProfileRead,
    StudentProfileUpdate,
)
from schemas.api.student_results import (
    StudentResultCreate,
    StudentResultRead,
    StudentResultUpdate,
)
from schemas.api.subjects import SubjectCreate, SubjectRead, SubjectUpdate
from schemas.api.tags import TagCreate, TagRead, TagUpdate
from schemas.api.test_library import (
    TestLibraryCreate,
    TestLibraryRead,
    TestLibraryUpdate,
)
from schemas.api.tutor_certifications import (
    TutorCertificationCreate,
    TutorCertificationRead,
    TutorCertificationUpdate,
)
from schemas.api.tutor_profiles import (
    TutorProfileCreate,
    TutorProfileRead,
    TutorProfileUpdate,
)
from schemas.api.tutor_tags import TutorTagCreate, TutorTagRead
from schemas.api.users import UserRead

__all__ = [
    "RegisterRequest",
    "RegisterResponse",
    "SubjectCreate",
    "SubjectRead",
    "SubjectUpdate",
    "TagCreate",
    "TagRead",
    "TagUpdate",
    "UserRead",
    "TutorProfileCreate",
    "TutorProfileRead",
    "TutorProfileUpdate",
    "StudentProfileCreate",
    "StudentProfileRead",
    "StudentProfileUpdate",
    "TutorTagCreate",
    "TutorTagRead",
    "StudentPreferredTagCreate",
    "StudentPreferredTagRead",
    "TutorCertificationCreate",
    "TutorCertificationRead",
    "TutorCertificationUpdate",
    "ScheduleCreate",
    "ScheduleRead",
    "ScheduleUpdate",
    "LessonCreate",
    "LessonRead",
    "LessonUpdate",
    "ApplicationCreate",
    "ApplicationRead",
    "ApplicationUpdate",
    "ChatRead",
    "MessageCreate",
    "MessageRead",
    "MessageUpdate",
    "TestLibraryCreate",
    "TestLibraryRead",
    "TestLibraryUpdate",
    "StudentResultCreate",
    "StudentResultRead",
    "StudentResultUpdate",
    "ReviewCreate",
    "ReviewRead",
    "ReviewUpdate",
    "DeviceTokenCreate",
    "DeviceTokenRead",
]
