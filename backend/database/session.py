"""
Database session management.
Using SQLAlchemy 2.0 with asynchronous support (aiosqlite).
"""
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base

from backend.config.settings import settings

# Base class for SQLAlchemy models
Base = declarative_base()

# Create Async Engine
# echo=False disables query logging (set to True for DB debugging)
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

# Async Session Factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for database sessions."""
    async with AsyncSessionLocal() as session:
        yield session

async def init_db():
    """Create all tables if they don't exist."""
    async with engine.begin() as conn:
        # Create all tables (does not handle migrations; fine for this spec)
        await conn.run_sync(Base.metadata.create_all)
