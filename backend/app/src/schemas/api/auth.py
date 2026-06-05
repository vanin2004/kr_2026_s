"""Auth (registration) Pydantic schemas."""

from uuid import UUID

from pydantic import BaseModel, field_validator, model_validator


class RegisterRequest(BaseModel):
    username: str
    password: str
    full_name: str
    role: str  # "tutor" | "student"
    subject_id: UUID | None = None
    hourly_rate: int | None = None

    @field_validator("role")
    @classmethod
    def role_must_be_valid(cls, v: str) -> str:
        if v not in ("tutor", "student"):
            raise ValueError("role must be 'tutor' or 'student'")
        return v

    @model_validator(mode="after")
    def check_tutor_fields(self) -> "RegisterRequest":
        if self.role == "tutor":
            if self.subject_id is None:
                raise ValueError("subject_id is required for tutors")
            if self.hourly_rate is None:
                raise ValueError("hourly_rate is required for tutors")
            if self.hourly_rate is not None and self.hourly_rate <= 0:
                raise ValueError("hourly_rate must be positive")
        return self


class RegisterResponse(BaseModel):
    user_id: str
    username: str
    role: str
