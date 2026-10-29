"""Core configuration and settings for SoulSync."""
from pathlib import Path
# pyrefly: ignore [missing-import]
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """Application settings loaded from environment and .env file."""

    # Application metadata
    APP_NAME: str = "SoulSync AI Assistant"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    # AI Service Settings
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-3.8-flash"
    EMBEDDING_MODEL: str = "text-embedding-005"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/soulsync_db"

    # Search Provider
    WEB_SEARCH_API_KEY: str = ""

    # CORS
    FRONTEND_ORIGIN: str = "http://localhost:5173"

    # File Uploads
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE_MB: int = 10

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def max_upload_size_bytes(self) -> int:
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    @property
    def upload_path(self) -> Path:
        p = BASE_DIR / self.UPLOAD_DIR
        p.mkdir(parents=True, exist_ok=True)
        return p


settings = Settings()
