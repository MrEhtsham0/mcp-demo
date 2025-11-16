"""
Database configuration and connection management
"""
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from typing import AsyncGenerator
from config import settings

# Create async engine with connection pooling
async_engine = create_async_engine(
    settings.async_database_url, 
    echo=settings.debug,
    # Connection pool settings
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_max_overflow,
    pool_timeout=settings.database_pool_timeout,
    pool_recycle=settings.database_pool_recycle,
    pool_pre_ping=True,
    # Connection settings
    connect_args={
        "charset": "utf8mb4",
        "autocommit": False,
    }
)

async def init_db_async():
    """Initialize database with SQLModel"""
    try:
        # Create all tables
        async with async_engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
        print("Database initialized successfully")
    except Exception as e:
        print(f"Database initialization error: {e}")
        raise

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Get async database session"""
    async with AsyncSession(async_engine) as session:
        yield session
