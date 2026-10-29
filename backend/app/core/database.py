"""Database connection, session management, and health checks."""
import logging
from typing import AsyncGenerator
# pyrefly: ignore [missing-import]
from sqlalchemy import text
# pyrefly: ignore [missing-import]
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings, BASE_DIR

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    """Base model class for all SQLAlchemy declarative models."""
    pass


# Initialize async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
    class_=AsyncSession,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for yielding database sessions."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def check_db_connection() -> dict:
    """
    Test database connectivity and return status.
    Gracefully reports whether database is connected or reachable.
    """
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
            return {"status": "connected", "database": "healthy"}
    except Exception as exc:
        logger.warning(f"Database health check failed: {exc}")
        return {"status": "disconnected", "error": str(exc)}


async def init_db() -> None:
    """
    Initialize database schemas and extensions.
    Enables pgvector extension if connected to PostgreSQL.
    Gracefully falls back to local SQLite if PostgreSQL is unreachable.
    """
    global engine, AsyncSessionLocal
    try:
        # Import models so Base.metadata is fully populated with all table schemas
        import app.models  # noqa: F401

        async with engine.begin() as conn:
            # If PostgreSQL, enable pgvector extension
            if "postgresql" in settings.DATABASE_URL:
                try:
                    await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                except Exception as ext_err:
                    logger.warning(f"Could not enable pgvector extension: {ext_err}")
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables initialized successfully.")
    except Exception as exc:
        if "postgresql" in settings.DATABASE_URL:
            logger.warning(
                f"PostgreSQL connection failed ({exc}). "
                "Automatically switching to local SQLite database (soulsync.db)..."
            )
            sqlite_path = BASE_DIR / "soulsync.db"
            sqlite_url = f"sqlite+aiosqlite:///{sqlite_path.resolve()}"
            engine = create_async_engine(sqlite_url, echo=settings.DEBUG)
            AsyncSessionLocal.configure(bind=engine)

            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info(f"Local SQLite database initialized successfully at: {sqlite_path}")
        else:
            logger.error(f"Database initialization error: {exc}")
