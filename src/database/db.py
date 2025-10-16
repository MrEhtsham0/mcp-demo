from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from typing import AsyncGenerator
from config import settings

# Create async engine using settings with connection pooling
async_engine = create_async_engine(
    settings.async_database_url, 
    echo=settings.debug,
    # Connection pool settings
    pool_size=10,                    # Number of connections to maintain in the pool
    max_overflow=20,                 # Additional connections that can be created beyond pool_size
    pool_timeout=30,                 # Seconds to wait for a connection from the pool
    pool_recycle=3600,               # Recycle connections after 1 hour (3600 seconds)
    pool_pre_ping=True,              # Validate connections before use
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