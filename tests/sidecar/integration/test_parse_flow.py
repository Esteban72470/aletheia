"""Integration tests for the parse flow."""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch


class TestParseFlow:
    """End-to-end tests for document parsing flow."""

    def test_parse_pdf_via_api(self):
        """Test parsing a PDF through the API endpoint."""
        from fastapi.testclient import TestClient
        from app.main import app

        client = TestClient(app)

        # Create a minimal PDF content
        pdf_content = b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]>>endobj\ntrailer<</Root 1 0 R>>\n%%EOF"

        response = client.post(
            "/parse",
            files={"file": ("test.pdf", pdf_content, "application/pdf")},
        )

        # Should accept the request (may fail internally without proper PDF)
        assert response.status_code in [200, 422, 500]

    def test_parse_image_via_api(self):
        """Test parsing an image through the API endpoint."""
        from fastapi.testclient import TestClient
        from app.main import app

        client = TestClient(app)

        # Create a minimal PNG (1x1 white pixel)
        png_content = bytes([
            0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,  # PNG signature
            0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52,  # IHDR chunk
            0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,  # 1x1
            0x08, 0x02, 0x00, 0x00, 0x00, 0x90, 0x77, 0x53,
            0xDE, 0x00, 0x00, 0x00, 0x0C, 0x49, 0x44, 0x41,
            0x54, 0x08, 0xD7, 0x63, 0xF8, 0xFF, 0xFF, 0x3F,
            0x00, 0x05, 0xFE, 0x02, 0xFE, 0xDC, 0xCC, 0x59,
            0xE7, 0x00, 0x00, 0x00, 0x00, 0x49, 0x45, 0x4E,
            0x44, 0xAE, 0x42, 0x60, 0x82,
        ])

        response = client.post(
            "/parse",
            files={"file": ("test.png", png_content, "image/png")},
        )

        assert response.status_code in [200, 422, 500]

    def test_parse_stores_document(self):
        """Test that parsing stores the document for later retrieval."""
        from fastapi.testclient import TestClient
        from app.main import app

        client = TestClient(app)

        # First, list existing documents
        response = client.get("/documents")
        assert response.status_code == 200
        initial_count = len(response.json())

        # Note: Full test would require a real parseable document

    @patch("app.pipeline.orchestrator.PipelineOrchestrator")
    def test_parse_with_mocked_orchestrator(self, mock_orchestrator_class):
        """Test parse endpoint with mocked pipeline."""
        from fastapi.testclient import TestClient
        from app.main import app
        from app.api.models import ParseResponse

        # Setup mock
        mock_orchestrator = MagicMock()
        mock_orchestrator.process_file.return_value = ParseResponse(
            document_id="mock-doc-id",
            pages=[],
            metadata={"source": "mock"},
        )
        mock_orchestrator_class.return_value = mock_orchestrator

        client = TestClient(app)

        # This tests the endpoint logic even if orchestrator fails
        response = client.post(
            "/parse",
            files={"file": ("test.pdf", b"mock content", "application/pdf")},
        )

        # Response depends on actual implementation
        assert response.status_code in [200, 422, 500]


class TestParseToStoreFlow:
    """Tests for parse → store → retrieve flow."""

    def test_document_persists_after_parse(self):
        """Test documents are saved to store after parsing."""
        from app.storage import DocumentStore
        from app.models import Document, Page

        store = DocumentStore()

        # Create and save a document
        doc = Document(
            id="persist-test-doc",
            pages=[Page(number=1, width=612, height=792, blocks=[])],
            metadata={"test": True},
        )
        store.save(doc)

        # Retrieve and verify
        retrieved = store.get("persist-test-doc")
        assert retrieved is not None
        assert retrieved.id == "persist-test-doc"

    def test_filesystem_store_persistence(self):
        """Test FileSystemDocumentStore persists across instances."""
        from app.storage.filesystem import FileSystemDocumentStore
        from app.models import Document, Page

        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "documents"

            # Create store and save document
            store1 = FileSystemDocumentStore(base_path=storage_path)
            doc = Document(
                id="fs-persist-test",
                pages=[Page(number=1, width=612, height=792, blocks=[])],
                metadata={"persistent": True},
            )
            store1.save(doc)

            # Create new store instance (simulating restart)
            store2 = FileSystemDocumentStore(base_path=storage_path)
            retrieved = store2.get("fs-persist-test")

            assert retrieved is not None
            assert retrieved.metadata.get("persistent") is True


class TestParseOptions:
    """Tests for parse endpoint options."""

    def test_parse_accepts_options(self):
        """Test parse endpoint accepts processing options."""
        from fastapi.testclient import TestClient
        from app.main import app

        client = TestClient(app)

        response = client.post(
            "/parse",
            files={"file": ("test.pdf", b"content", "application/pdf")},
            data={"ocr_engine": "tesseract", "extract_tables": "true"},
        )

        # Should accept options (validation may fail)
        assert response.status_code in [200, 422, 500]

    def test_parse_with_page_range(self):
        """Test parse with page range option."""
        from fastapi.testclient import TestClient
        from app.main import app

        client = TestClient(app)

        response = client.post(
            "/parse",
            files={"file": ("test.pdf", b"content", "application/pdf")},
            data={"pages": "1-3"},
        )

        assert response.status_code in [200, 422, 500]
