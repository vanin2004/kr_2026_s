import enum


class UserRole(str, enum.Enum):
    tutor = "tutor"
    student = "student"


class LessonStatus(str, enum.Enum):
    planned = "planned"
    completed = "completed"
    cancelled = "cancelled"


class ApplicationStatus(str, enum.Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"


class ResultType(str, enum.Enum):
    initial_test = "initial_test"
    control_test = "control_test"


class DevicePlatform(str, enum.Enum):
    android = "android"
    ios = "ios"
