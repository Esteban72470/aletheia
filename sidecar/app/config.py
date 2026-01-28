"""Application configuration."""

from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Environment
    environment: str = "development"
    debug: bool = False

    # Server
    host: str = "127.0.0.1"
    port: int = 8420

    # Paths
    cache_dir: Path = Path.home() / ".cache" / "aletheia"
    models_dir: Path = Path.home() / ".local" / "share" / "aletheia" / "models"

    # CORS
    allowed_origins: List[str] = ["http://localhost:*", "vscode-webview://*"]

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"

    # Processing
    max_file_size_mb: int = 100
    default_dpi: int = 300
    max_pages: int = 500

    # OCR
    default_ocr_engine: str = "tesseract"
    tesseract_lang: str = "eng"

    # Cache
    cache_enabled: bool = True
    cache_ttl_hours: int = 24

    class Config:
        env_prefix = "ALETHEIA_"
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
