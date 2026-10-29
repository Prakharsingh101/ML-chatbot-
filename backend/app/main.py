"""FastAPI application entry point for SoulSync AI Assistant."""
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator
# pyrefly: ignore [missing-import]
from fastapi import FastAPI
# pyrefly: ignore [missing-import]
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_db
from app.api import chat, conversations, documents, health

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
)
logger = logging.getLogger("soulsync.main")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifecycle manager.
    Runs database schema initialization on startup.
    """
    logger.info("Initializing SoulSync backend services...")
    try:
        await init_db()
        logger.info("Database schemas and extensions checked/initialized successfully.")
    except Exception as exc:
        logger.error(f"Failed during database startup initialization: {exc}")
    
    yield
    
    logger.info("SoulSync backend shutting down.")


# Initialize FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Multimodal emotional AI companion API powered by FastAPI, PostgreSQL (pgvector), and Google Gemini.",
    debug=settings.DEBUG,
    lifespan=lifespan,
)

# CORS setup
allowed_origins = {
    settings.FRONTEND_ORIGIN.rstrip("/"),
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
}

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(allowed_origins),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/", tags=["General"])
async def root() -> dict:
    """Root endpoint verifying API availability."""
    return {
        "status": "online",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "documentation": "/docs",
    }

# Register Routers (registered at root and /api for compatibility)
app.include_router(health.router)
app.include_router(chat.router)
app.include_router(conversations.router)
app.include_router(documents.router)

# Also expose under /api prefix for standard client setups
app.include_router(health.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(conversations.router, prefix="/api")
app.include_router(documents.router, prefix="/api")

