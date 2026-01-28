"""Health check endpoint."""

from datetime import datetime
from typing import Dict, List

from fastapi import APIRouter

router = APIRouter()

# Track startup time
_startup_time = datetime.utcnow()


@router.get("/health")
async def health_check() -> Dict:
    """Return health status and basic info."""
    uptime = (datetime.utcnow() - _startup_time).total_seconds()

    return {
        "status": "healthy",
        "version": "0.1.0",
        "uptime_seconds": int(uptime),
        "models_loaded": get_loaded_models(),
    }


def get_loaded_models() -> List[str]:
    """Get list of currently loaded models.

    Checks which models have been initialized and are ready for inference.
    """
    loaded = []

    # Check Tesseract availability
    try:
        import pytesseract
        pytesseract.get_tesseract_version()
        loaded.append("tesseract")
    except Exception:
        pass

    # Check if PIL/Pillow is available for image processing
    try:
        from PIL import Image
        loaded.append("pillow")
    except ImportError:
        pass

    # Check PyMuPDF for PDF processing
    try:
        import fitz
        loaded.append("pymupdf")
    except ImportError:
        pass

    return loaded if loaded else ["none"]
