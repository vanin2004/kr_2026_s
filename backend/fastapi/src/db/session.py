import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from src.config import settings

logger = logging.getLogger(__name__)

# SQLAlchemy requires postgresql+asyncpg:// for async connections
SQLALCHEMY_DATABASE_URL = settings.database_url.replace("postgresql://", "postgresql+asyncpg://")

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=False,
    future=True,
    pool_size=20,
    max_overflow=10
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
