"""OCR module for text extraction."""

from app.pipeline.ocr.ocr_base import BaseOCR
from app.pipeline.ocr.tesseract_backend import TesseractBackend
from app.pipeline.ocr.trocr_backend import TrOCRBackend

__all__ = ["BaseOCR", "TesseractBackend", "TrOCRBackend"]
