import asyncio
from contextlib import asynccontextmanager

from api.endpoints import auth, crud, internal, suggestions
from db.seed import seed_database
from db.session import async_engine
from fastapi import FastAPI
from models.base import Base
from services.notifications import notification_service
from sqlalchemy import text


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        async with async_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))

        print("Creating tables from ORM models …")
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        print("Database connection established")
        await seed_database()
    except Exception as e:
        print(f"Warning: Could not connect to database: {e}")

    # Start NOTIFY listener in background
    asyncio.create_task(notification_service.start_listener())
    yield
    # Shutdown
    notification_service.stop_event.set()
    await async_engine.dispose()


app = FastAPI(title="TutorApp API", lifespan=lifespan)

# Include routers
app.include_router(auth.router, prefix="/api/custom", tags=["auth"])
app.include_router(suggestions.router, prefix="/api/custom", tags=["suggestions"])
app.include_router(internal.router, prefix="/api/custom/internal", tags=["internal"])
app.include_router(crud.router, prefix="/api/custom", tags=["crud"])


@app.get("/health")
async def health_check():
    return {"status": "ok"}
