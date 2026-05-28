import logging

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from ...db.session import db_pool

router = APIRouter()
logger = logging.getLogger(__name__)

class KeycloakUserCreated(BaseModel):
    userId: str
    email: str
    realmRole: str

@router.post("/user-created", status_code=status.HTTP_201_CREATED)
async def user_created(user: KeycloakUserCreated):
    try:
        # 1. Insert into users table
        await db_pool.execute(
            "INSERT INTO users (id, email, role) VALUES ($1, $2, $3) ON CONFLICT (id) DO NOTHING",
            user.userId, user.email, user.realmRole
        )
        
        # 2. Insert empty profile
        if user.realmRole == 'tutor':
            await db_pool.execute(
                "INSERT INTO tutor_profiles (user_id) VALUES ($1) ON CONFLICT (user_id) DO NOTHING",
                user.userId
            )
        elif user.realmRole == 'student':
            await db_pool.execute(
                "INSERT INTO student_profiles (user_id) VALUES ($1) ON CONFLICT (user_id) DO NOTHING",
                user.userId
            )
            
        return {"status": "created"}
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail=str(e))
