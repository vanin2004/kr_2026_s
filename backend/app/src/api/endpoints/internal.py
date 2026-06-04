import logging
import uuid

from db.session import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from models.enums import UserRole
from models.tables import StudentProfile, TutorProfile, User
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()
logger = logging.getLogger(__name__)


class KeycloakUserCreated(BaseModel):
    userId: str
    email: str
    realmRole: str


@router.post("/user-created", status_code=status.HTTP_201_CREATED)
async def user_created(
    user: KeycloakUserCreated,
    db: AsyncSession = Depends(get_db),
):
    """
    Called by Keycloak Event Listener webhook when a new user registers.
    Creates user record + empty profile (tutor or student).
    """
    try:
        try:
            user_id = (
                uuid.UUID(user.userId) if isinstance(user.userId, str) else user.userId
            )
        except ValueError:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid userId: '{user.userId}' is not a valid UUID",
            )

        # Check if user already exists
        existing = await db.execute(select(User).where(User.id == user_id))
        if existing.scalar_one_or_none():
            return {"status": "already_exists"}

        # Validate role
        try:
            role = UserRole(user.realmRole)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid role: {user.realmRole}. Must be 'tutor' or 'student'",
            )

        # 1. Insert user
        db_user = User(id=user_id, email=user.email, role=role)
        db.add(db_user)

        # 2. Insert empty profile
        if role == UserRole.tutor:
            db.add(TutorProfile(user_id=user_id))
        elif role == UserRole.student:
            db.add(StudentProfile(user_id=user_id))

        await db.flush()

        logger.info(f"User created: id={user_id}, email={user.email}, role={role}")
        return {"status": "created"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail=str(e))
