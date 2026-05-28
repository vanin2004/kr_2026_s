"""
FastAPI main application entry point
"""

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.endpoints import router as custom_router
from src.auth.deps import verify_token
from src.db.session import get_db

app = FastAPI(
    title="Tutor Platform API",
    description="API for tutor matching and lesson planning platform",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(custom_router, prefix="/api/custom", tags=["custom_logic"])


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "tutor-platform-api"}


@app.get("/api/custom/db-check")
async def database_check(db: AsyncSession = Depends(get_db)):
    """Check database connection"""
    try:
        result = await db.execute(text("SELECT 1"))
        return {"status": "ok", "db_alive": result.scalar() == 1}
    except Exception as e:
        return {"status": "error", "detail": str(e)}

@app.get("/api/custom/auth-check")
async def auth_check(token_payload: dict = Depends(verify_token)):
    """Check user token"""
    return {"status": "ok", "user_id": token_payload.get("sub"), "roles": token_payload.get("realm_access", {}).get("roles", [])}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
