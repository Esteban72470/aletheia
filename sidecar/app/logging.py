"""Logging configuration."""

import logging
import sys
from typing import Optional

from app.config import settings


def setup_logging(level: Optional[str] = None) -> None:
    """Configure application logging."""
    log_level = getattr(logging, level or settings.log_level.upper())

    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    # Set third-party loggers to WARNING
    for logger_name in ["uvicorn", "httpx", "PIL"]:
        logging.getLogger(logger_name).setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(name)
