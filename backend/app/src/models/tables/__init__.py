"""SQLAlchemy ORM models for all database tables — package.

Re-exports all model classes from domain-specific submodules
for backward compatibility (from models.tables import <Model>).
"""

from models.tables.application import Application, Chat, Message
from models.tables.device import DeviceToken
from models.tables.lesson import Lesson
from models.tables.review import Review
from models.tables.schedule import Schedule
from models.tables.subject import Subject, Tag
from models.tables.test_library import StudentResult, TestLibrary
from models.tables.tutor_relationship import (
    StudentPreferredTag,
    TutorCertification,
    TutorTag,
)
from models.tables.user import StudentProfile, TutorProfile, User

__all__ = [
    "Subject",
    "Tag",
    "User",
    "TutorProfile",
    "StudentProfile",
    "TutorTag",
    "StudentPreferredTag",
    "TutorCertification",
    "Schedule",
    "Lesson",
    "Application",
    "Chat",
    "Message",
    "TestLibrary",
    "StudentResult",
    "Review",
    "DeviceToken",
]
