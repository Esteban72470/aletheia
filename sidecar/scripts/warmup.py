#!/usr/bin/env python3
"""Warmup script to preload models and cache."""

import sys
import time
from pathlib import Path

# Add sidecar to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def warmup():
    """Warmup models and caches."""
    print("Warming up Aletheia sidecar...")
    start_time = time.time()

    # Load OCR engine
    print("  Loading OCR engine...")
    try:
        import pytesseract
        version = pytesseract.get_tesseract_version()
        print(f"    ✓ Tesseract {version} loaded")
    except Exception as e:
        print(f"    ✗ Tesseract not available: {e}")

    # Load PDF library
    print("  Loading PDF library...")
    try:
        import fitz
        print(f"    ✓ PyMuPDF {fitz.version[0]} loaded")
    except ImportError as e:
        print(f"    ✗ PyMuPDF not available: {e}")

    # Load image library
    print("  Loading image library...")
    try:
        from PIL import Image
        print(f"    ✓ Pillow loaded")
    except ImportError as e:
        print(f"    ✗ Pillow not available: {e}")

    # Initialize pipeline orchestrator
    print("  Initializing pipeline...")
    try:
        from app.pipeline.orchestrator import PipelineOrchestrator
        orchestrator = PipelineOrchestrator()
        print(f"    ✓ Pipeline ready with {len(orchestrator.loaders)} loaders")
    except Exception as e:
        print(f"    ✗ Pipeline initialization failed: {e}")

    # Prime document store
    print("  Initializing document store...")
    try:
        from app.storage import DocumentStore
        store = DocumentStore()
        print(f"    ✓ Document store ready")
    except Exception as e:
        print(f"    ✗ Document store failed: {e}")

    elapsed = time.time() - start_time
    print(f"\nWarmup complete in {elapsed:.2f}s!")


if __name__ == "__main__":
    warmup()
