from typing import AsyncGenerator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings

settings = get_settings()

# Async engine for FastAPI endpoints
engine = create_async_engine(settings.DATABASE_URL, echo=settings.ENV == "development")

async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Sync engine for AG2 tools (runs in a synchronous thread)
sync_engine = create_engine(settings.SYNC_DATABASE_URL, echo=settings.ENV == "development")
SyncSessionLocal = sessionmaker(bind=sync_engine)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

