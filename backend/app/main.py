import asyncio

from fastapi import FastAPI

from .api.endpoints import internal, suggestions
from .db.session import db_pool
from .services.notifications import notification_service

app = FastAPI(title="TutorApp Custom Logic API")

@app.on_event("startup")
async def startup():
    await db_pool.connect()
    asyncio.create_task(notification_service.start_listener())

@app.on_event("shutdown")
async def shutdown():
    notification_service.stop_event.set()
    await db_pool.disconnect()

# Include routers
app.include_router(suggestions.router, prefix="/api/custom", tags=["suggestions"])
app.include_router(internal.router, prefix="/api/custom/internal", tags=["internal"])

@app.get("/health")
async def health_check():
    return {"status": "ok"}
