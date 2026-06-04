import logging
import uuid
from decimal import Decimal
from typing import Any, Optional

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


class WebhookRequest(BaseModel):
    """
    Модель запроса от com.vymalo keycloak-webhook-provider.
    Отправляется POST на {basePath}/sendWebhook.
    """

    type: str
    realmId: Optional[str] = None
    id: Optional[str] = None
    time: Optional[Decimal] = None
    clientId: Optional[str] = None
    userId: Optional[str] = None
    ipAddress: Optional[str] = None
    error: Optional[str] = None
    details: Optional[dict[str, Any]] = None
    resourcePath: Optional[str] = None
    representation: Optional[str] = None


async def _create_user_from_webhook(
    user_id: str,
    email: str,
    realm_role: str,
    db: AsyncSession,
) -> dict:
    """
    Создаёт пользователя и пустой профиль (tutor или student).
    """
    try:
        uid = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid userId: '{user_id}' is not a valid UUID",
        )

    existing = await db.execute(select(User).where(User.id == uid))
    if existing.scalar_one_or_none():
        return {"status": "already_exists"}

    try:
        role = UserRole(realm_role)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid role: {realm_role}. Must be 'tutor' or 'student'",
        )

    db_user = User(id=uid, email=email, role=role)
    db.add(db_user)

    if role == UserRole.tutor:
        db.add(TutorProfile(user_id=uid))
    elif role == UserRole.student:
        db.add(StudentProfile(user_id=uid))

    await db.flush()

    logger.info(f"User created: id={uid}, email={email}, role={role}")
    return {"status": "created"}


@router.post("", status_code=status.HTTP_200_OK)
@router.post("/sendWebhook", status_code=status.HTTP_200_OK)
async def send_webhook(
    payload: WebhookRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Эндпоинт для com.vymalo keycloak-webhook-provider.
    Принимает события Keycloak (REGISTER, LOGIN, LOGOUT, и т.д.) на / и /sendWebhook.
    Для REGISTER извлекает userId, email и realmRole из details и создаёт пользователя.
    """
    logger.info(f"Webhook received: type={payload.type}, userId={payload.userId}")

    if payload.type == "REGISTER":
        if not payload.userId:
            logger.warning("REGISTER event without userId, skipping")
            return {"status": "skipped", "reason": "missing userId"}

        email = ""
        realm_role = "student"

        if payload.details:
            email = payload.details.get("email", "")
            realm_role = payload.details.get("realm_role", "student")

        try:
            result = await _create_user_from_webhook(
                user_id=payload.userId,
                email=email,
                realm_role=realm_role,
                db=db,
            )
            return result
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error processing REGISTER webhook: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    # Для LOGIN — создаём пользователя, если его ещё нет в БД
    # (например, если пользователь был импортирован через realm-config
    #  или зарегистрирован, пока вебхук не работал)
    if payload.type == "LOGIN":
        if not payload.userId:
            logger.warning("LOGIN event without userId, skipping")
            return {"status": "skipped", "reason": "missing userId"}

        # Проверяем, существует ли уже пользователь
        try:
            uid = (
                uuid.UUID(payload.userId)
                if isinstance(payload.userId, str)
                else payload.userId
            )
            existing = await db.execute(select(User).where(User.id == uid))
            if existing.scalar_one_or_none():
                logger.info(f"User {uid} already exists, nothing to do on LOGIN")
                return {"status": "already_exists"}
        except ValueError:
            logger.warning(f"Invalid userId in LOGIN event: {payload.userId}")
            return {"status": "skipped", "reason": "invalid userId"}

        # Пользователя нет — создаём (как при REGISTER)
        email = ""
        realm_role = "student"

        if payload.details:
            email = payload.details.get("email", "")
            realm_role = payload.details.get("realm_role", "student")

        try:
            result = await _create_user_from_webhook(
                user_id=payload.userId,
                email=email,
                realm_role=realm_role,
                db=db,
            )
            logger.info(f"User {uid} created on LOGIN event (was missing in DB)")
            return result
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating user on LOGIN webhook: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    # Для остальных событий (LOGOUT, UPDATE_PROFILE, DELETE_ACCOUNT)
    # просто подтверждаем получение
    logger.info(f"Webhook event {payload.type} acknowledged")
    return {"status": "acknowledged", "event": payload.type}


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
        result = await _create_user_from_webhook(
            user_id=user.userId,
            email=user.email,
            realm_role=user.realmRole,
            db=db,
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail=str(e))
