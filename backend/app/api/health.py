"""Health check endpoint."""
# pyrefly: ignore [missing-import]
from fastapi import APIRouter
from app.core.config import settings
from app.core.database import check_db_connection
from app.services.ai_service import ai_service

router = APIRouter(tags=["Health"])


@router.get("/health", summary="Application health and dependencies check")
async def get_health() -> dict:
    """
    Check the overall health of the API server, database connection,
    and configured AI providers.
    """
    db_status = await check_db_connection()
    return {
        "status": "healthy" if db_status.get("status") == "connected" else "degraded",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "database": db_status,
        "gemini_configured": ai_service.is_configured(),
        "search_configured": bool(settings.WEB_SEARCH_API_KEY.strip()),
    }
