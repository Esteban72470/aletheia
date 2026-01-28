"""Unit tests for pipeline components."""

import pytest
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path


class TestPDFLoader:
    """Tests for PDFLoader class."""

    def test_can_handle_pdf_file(self):
        """Test PDF loader accepts .pdf files."""
        from app.pipeline.ingest.loaders.pdf import PDFLoader

        loader = PDFLoader()
        assert loader.can_handle(Path("document.pdf")) is True
        assert loader.can_handle(Path("path/to/file.PDF")) is True

    def test_cannot_handle_non_pdf_file(self):
        """Test PDF loader rejects non-pdf files."""
        from app.pipeline.ingest.loaders.pdf import PDFLoader

        loader = PDFLoader()
        assert loader.can_handle(Path("document.txt")) is False
        assert loader.can_handle(Path("image.png")) is False
        assert loader.can_handle(Path("doc.docx")) is False

    @patch("app.pipeline.ingest.loaders.pdf.fitz")
    def test_load_creates_raw_pages(self, mock_fitz):
        """Test loading PDF creates RawPage objects."""
        from app.pipeline.ingest.loaders.pdf import PDFLoader

        # Setup mock PDF document
        mock_page = MagicMock()
        mock_page.get_text.return_value = "Page content"
        mock_page.get_pixmap.return_value = MagicMock(
            tobytes=lambda: b"fake_image_bytes"
        )
        mock_page.rect = MagicMock(width=612, height=792)

        mock_doc = MagicMock()
        mock_doc.__iter__ = lambda self: iter([mock_page])
        mock_doc.__len__ = lambda self: 1
        mock_fitz.open.return_value = mock_doc

        loader = PDFLoader()
        pages = loader.load(Path("test.pdf"))

        assert len(pages) == 1
        mock_fitz.open.assert_called_once()


class TestImageLoader:
    """Tests for ImageLoader class."""

    def test_can_handle_image_files(self):
        """Test image loader accepts common image formats."""
        from app.pipeline.ingest.loaders.image import ImageLoader

        loader = ImageLoader()
        assert loader.can_handle(Path("photo.png")) is True
        assert loader.can_handle(Path("photo.jpg")) is True
        assert loader.can_handle(Path("photo.jpeg")) is True
        assert loader.can_handle(Path("photo.tiff")) is True
        assert loader.can_handle(Path("photo.bmp")) is True

    def test_cannot_handle_non_image_files(self):
        """Test image loader rejects non-image files."""
        from app.pipeline.ingest.loaders.image import ImageLoader

        loader = ImageLoader()
        assert loader.can_handle(Path("document.pdf")) is False
        assert loader.can_handle(Path("file.txt")) is False
        assert loader.can_handle(Path("script.py")) is False


class TestTesseractBackend:
    """Tests for Tesseract OCR backend."""

    @patch("app.pipeline.ocr.tesseract.pytesseract")
    def test_process_returns_word_boxes(self, mock_pytesseract):
        """Test OCR processing returns word bounding boxes."""
        from app.pipeline.ocr.tesseract import TesseractBackend

        # Mock pytesseract output
        mock_pytesseract.image_to_data.return_value = {
            "text": ["Hello", "World", ""],
            "left": [10, 100, 0],
            "top": [20, 20, 0],
            "width": [50, 60, 0],
            "height": [15, 15, 0],
            "conf": [95, 90, -1],
        }

        backend = TesseractBackend()
        mock_image = MagicMock()

        results = backend.process(mock_image)

        assert len(results) == 2  # Empty text filtered out
        assert results[0]["text"] == "Hello"
        assert results[1]["text"] == "World"


class TestPipelineOrchestrator:
    """Tests for PipelineOrchestrator class."""

    def test_orchestrator_initialization(self):
        """Test orchestrator initializes with default loaders."""
        from app.pipeline.orchestrator import PipelineOrchestrator

        orchestrator = PipelineOrchestrator()
        assert orchestrator.loaders is not None
        assert len(orchestrator.loaders) >= 2  # PDF and Image loaders

    def test_find_loader_for_pdf(self):
        """Test orchestrator finds correct loader for PDF."""
        from app.pipeline.orchestrator import PipelineOrchestrator

        orchestrator = PipelineOrchestrator()
        loader = orchestrator._find_loader(Path("test.pdf"))

        assert loader is not None
        assert "PDF" in type(loader).__name__

    def test_find_loader_for_image(self):
        """Test orchestrator finds correct loader for images."""
        from app.pipeline.orchestrator import PipelineOrchestrator

        orchestrator = PipelineOrchestrator()
        loader = orchestrator._find_loader(Path("test.png"))

        assert loader is not None
        assert "Image" in type(loader).__name__

    def test_find_loader_for_unsupported_type(self):
        """Test orchestrator returns None for unsupported file types."""
        from app.pipeline.orchestrator import PipelineOrchestrator

        orchestrator = PipelineOrchestrator()
        loader = orchestrator._find_loader(Path("test.xyz"))

        assert loader is None

    @patch("app.pipeline.orchestrator.PDFLoader")
    def test_process_file_pdf(self, mock_pdf_loader_class):
        """Test processing a PDF file."""
        from app.pipeline.orchestrator import PipelineOrchestrator
        from app.api.models import ParseResponse

        # Setup mock loader
        mock_loader = MagicMock()
        mock_loader.can_handle.return_value = True
        mock_loader.load.return_value = []
        mock_pdf_loader_class.return_value = mock_loader

        orchestrator = PipelineOrchestrator()
        orchestrator.loaders = [mock_loader]

        # Mock file path
        with patch("pathlib.Path.exists", return_value=True):
            result = orchestrator.process_file(Path("test.pdf"))

        assert isinstance(result, ParseResponse)

    def test_process_file_not_found(self):
        """Test processing non-existent file raises error."""
        from app.pipeline.orchestrator import PipelineOrchestrator

        orchestrator = PipelineOrchestrator()

        with pytest.raises(FileNotFoundError):
            orchestrator.process_file(Path("nonexistent.pdf"))


class TestPipelineStages:
    """Tests for individual pipeline stages."""

    def test_preprocess_stage_exists(self):
        """Test preprocess stage module exists."""
        from app.pipeline import preprocess
        assert preprocess is not None

    def test_layout_stage_exists(self):
        """Test layout stage module exists."""
        from app.pipeline import layout
        assert layout is not None

    def test_postprocess_stage_exists(self):
        """Test postprocess stage module exists."""
        from app.pipeline import postprocess
        assert postprocess is not None


class TestPipelineController:
    """Tests for PipelineController class."""

    def test_controller_initialization(self):
        """Test controller initializes properly."""
        from app.pipeline.controller import PipelineController

        controller = PipelineController()
        assert controller is not None

    def test_controller_has_orchestrator(self):
        """Test controller has access to orchestrator."""
        from app.pipeline.controller import PipelineController

        controller = PipelineController()
        # Controller should provide access to processing capabilities
        assert hasattr(controller, "process") or hasattr(controller, "orchestrator")
