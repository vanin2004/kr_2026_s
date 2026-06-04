from contextlib import asynccontextmanager
import asyncio
from api.endpoints import crud, internal, suggestions
from db.session import async_engine
from fastapi import FastAPI
from services.notifications import notification_service
from sqlalchemy import text


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        async with async_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        print("Database connection established")
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
app.include_router(suggestions.router, prefix="/api/custom", tags=["suggestions"])
app.include_router(internal.router, prefix="/api/custom/internal", tags=["internal"])
app.include_router(crud.router, prefix="/api/custom", tags=["crud"])


@app.get("/health")
async def health_check():
    return {"status": "ok"}
