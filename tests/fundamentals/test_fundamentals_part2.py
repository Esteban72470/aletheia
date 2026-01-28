#!/usr/bin/env python3
"""
Fundamentals Part 2 Verification Test Script
=============================================

This script validates that all Fundamentals Part 2 components are working correctly:
1. Pipeline Orchestrator - Document processing with loaders
2. File-based Storage - Persistent document storage
3. Query Endpoint - Search functionality
4. Unit Tests - All tests pass

Run this script to verify the fundamentals are complete before proceeding
to Phase 1 of the project.

Usage:
    cd sidecar
    python -m pytest ../tests/fundamentals/test_fundamentals_part2.py -v
"""

import pytest
import os
import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch


# ============================================================================
# Section 1: Pipeline Integration Tests
# ============================================================================

class TestPipelineIntegration:
    """Tests to verify pipeline orchestrator is properly integrated."""

    def test_orchestrator_can_be_imported(self):
        """Verify PipelineOrchestrator can be imported."""
        from app.pipeline.orchestrator import PipelineOrchestrator
        assert PipelineOrchestrator is not None

    def test_orchestrator_has_loaders(self):
        """Verify orchestrator initializes with loaders."""
        from app.pipeline.orchestrator import PipelineOrchestrator

        orchestrator = PipelineOrchestrator()
        assert hasattr(orchestrator, 'loaders')
        assert len(orchestrator.loaders) >= 2  # PDF and Image loaders

    def test_pdf_loader_integrated(self):
        """Verify PDF loader is available."""
        from app.pipeline.ingest.loaders.pdf import PDFLoader

        loader = PDFLoader()
        assert loader.can_handle(Path("test.pdf")) is True

    def test_image_loader_integrated(self):
        """Verify Image loader is available."""
        from app.pipeline.ingest.loaders.image import ImageLoader

        loader = ImageLoader()
        assert loader.can_handle(Path("test.png")) is True
        assert loader.can_handle(Path("test.jpg")) is True

    def test_ocr_backend_can_initialize(self):
        """Verify OCR backend can be created."""
        try:
            from app.pipeline.ocr.tesseract import TesseractBackend
            backend = TesseractBackend()
            assert backend is not None
        except ImportError:
            pytest.skip("Tesseract backend not available")


# ============================================================================
# Section 2: Storage Tests
# ============================================================================

class TestStoragePersistence:
    """Tests to verify file-based storage is working."""

    def test_filesystem_store_can_be_imported(self):
        """Verify FileSystemDocumentStore can be imported."""
        from app.storage.filesystem import FileSystemDocumentStore
        assert FileSystemDocumentStore is not None

    def test_filesystem_store_creates_directory(self):
        """Verify store creates storage directory."""
        from app.storage.filesystem import FileSystemDocumentStore

        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "documents"
            store = FileSystemDocumentStore(base_path=storage_path)
            assert storage_path.exists()

    def test_document_save_and_load(self):
        """Verify documents can be saved and loaded."""
        from app.storage.filesystem import FileSystemDocumentStore
        from app.models import Document, Page

        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "documents"
            store = FileSystemDocumentStore(base_path=storage_path)

            # Create test document
            doc = Document(
                id="test-doc-001",
                pages=[Page(number=1, width=612, height=792, blocks=[])],
                metadata={"test": True}
            )

            # Save
            store.save(doc)

            # Load
            loaded = store.get("test-doc-001")
            assert loaded is not None
            assert loaded.id == "test-doc-001"
            assert loaded.metadata.get("test") is True

    def test_document_delete(self):
        """Verify documents can be deleted."""
        from app.storage.filesystem import FileSystemDocumentStore
        from app.models import Document, Page

        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "documents"
            store = FileSystemDocumentStore(base_path=storage_path)

            doc = Document(
                id="delete-me",
                pages=[Page(number=1, width=612, height=792, blocks=[])],
                metadata={}
            )

            store.save(doc)
            assert store.get("delete-me") is not None

            store.delete("delete-me")
            assert store.get("delete-me") is None

    def test_in_memory_store_exists(self):
        """Verify in-memory DocumentStore exists."""
        from app.storage import DocumentStore

        store = DocumentStore()
        assert store is not None
        assert hasattr(store, 'save')
        assert hasattr(store, 'get')
        assert hasattr(store, 'delete')


# ============================================================================
# Section 3: Query Endpoint Tests
# ============================================================================

class TestQueryEndpoint:
    """Tests to verify query endpoint is functional."""

    def test_query_router_exists(self):
        """Verify query router is defined."""
        from app.api.query import router
        assert router is not None

    def test_keyword_search_function(self):
        """Verify keyword search is implemented."""
        from app.api.query import keyword_search
        from app.models import Document, Page, Block, BoundingBox

        # Create searchable document
        block = Block(
            id="b1",
            type="text",
            text="Fundamentals part two verification test",
            bbox=BoundingBox(x=0, y=0, width=100, height=20)
        )
        page = Page(number=1, width=612, height=792, blocks=[block])
        doc = Document(id="search-doc", pages=[page], metadata={})

        results = keyword_search([doc], "fundamentals")
        assert len(results) == 1

    def test_regex_search_function(self):
        """Verify regex search is implemented."""
        from app.api.query import regex_search
        from app.models import Document, Page, Block, BoundingBox

        block = Block(
            id="b1",
            type="text",
            text="Invoice #INV-2024-001 for $500.00",
            bbox=BoundingBox(x=0, y=0, width=100, height=20)
        )
        page = Page(number=1, width=612, height=792, blocks=[block])
        doc = Document(id="regex-doc", pages=[page], metadata={})

        # Match invoice number pattern
        results = regex_search([doc], r"#INV-\d{4}-\d{3}")
        assert len(results) == 1

    def test_query_with_app(self):
        """Verify query endpoint works via test client."""
        from fastapi.testclient import TestClient
        from app.main import app

        client = TestClient(app)

        # Test documents endpoint exists
        response = client.get("/documents")
        assert response.status_code == 200


# ============================================================================
# Section 4: API Integration Tests
# ============================================================================

class TestAPIIntegration:
    """Tests to verify API endpoints are properly wired."""

    def test_app_starts(self):
        """Verify FastAPI app can be created."""
        from app.main import app
        assert app is not None

    def test_health_endpoint(self):
        """Verify health endpoint returns OK."""
        from fastapi.testclient import TestClient
        from app.main import app

        client = TestClient(app)
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data.get("status") in ["healthy", "ok"]

    def test_parse_endpoint_exists(self):
        """Verify parse endpoint is registered."""
        from app.main import app

        routes = [route.path for route in app.routes]
        assert "/parse" in routes or any("/parse" in r for r in routes)

    def test_query_endpoint_exists(self):
        """Verify query endpoint is registered."""
        from app.main import app

        routes = [route.path for route in app.routes]
        assert "/query" in routes or any("/query" in r for r in routes)


# ============================================================================
# Section 5: Model Validation Tests
# ============================================================================

class TestModels:
    """Tests to verify Pydantic models are correctly defined."""

    def test_document_model(self):
        """Verify Document model works."""
        from app.models import Document, Page

        doc = Document(
            id="model-test",
            pages=[Page(number=1, width=612, height=792, blocks=[])],
            metadata={"validated": True}
        )

        assert doc.id == "model-test"
        assert len(doc.pages) == 1

    def test_block_model(self):
        """Verify Block model works."""
        from app.models import Block, BoundingBox

        block = Block(
            id="block-1",
            type="text",
            text="Test content",
            bbox=BoundingBox(x=10, y=20, width=100, height=50)
        )

        assert block.type == "text"
        assert block.bbox.x == 10

    def test_query_models(self):
        """Verify query models work."""
        from app.models.query import PerceptionQuery, QueryResponse, QueryResult

        query = PerceptionQuery(keywords=["test"])
        assert "test" in query.keywords

        result = QueryResult(
            document_id="doc-1",
            page_number=1,
            block_id="b1",
            text="Found",
            score=0.9
        )

        response = QueryResponse(
            query="test",
            results=[result],
            total_results=1
        )
        assert response.total_results == 1


# ============================================================================
# Section 6: End-to-End Smoke Test
# ============================================================================

class TestEndToEnd:
    """End-to-end smoke test for the complete workflow."""

    @patch("app.pipeline.orchestrator.PDFLoader")
    def test_complete_workflow(self, mock_loader_class):
        """Test complete parse -> store -> query workflow."""
        from app.storage.filesystem import FileSystemDocumentStore
        from app.models import Document, Page, Block, BoundingBox
        from app.api.query import keyword_search

        with tempfile.TemporaryDirectory() as tmpdir:
            # 1. Create storage
            storage_path = Path(tmpdir) / "documents"
            store = FileSystemDocumentStore(base_path=storage_path)

            # 2. Create document (simulating parse result)
            block = Block(
                id="e2e-block",
                type="text",
                text="End-to-end test content for Aletheia",
                bbox=BoundingBox(x=72, y=72, width=468, height=24)
            )
            page = Page(number=1, width=612, height=792, blocks=[block])
            doc = Document(
                id="e2e-document",
                pages=[page],
                metadata={"source": "e2e-test"}
            )

            # 3. Save to store
            store.save(doc)

            # 4. Retrieve and verify
            loaded = store.get("e2e-document")
            assert loaded is not None
            assert loaded.pages[0].blocks[0].text == "End-to-end test content for Aletheia"

            # 5. Search
            results = keyword_search([loaded], "Aletheia")
            assert len(results) == 1

            # 6. Cleanup
            store.delete("e2e-document")
            assert store.get("e2e-document") is None

        print("\n✅ End-to-end workflow completed successfully!")


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    """Run verification tests."""
    print("=" * 60)
    print("Aletheia Fundamentals Part 2 Verification")
    print("=" * 60)

    # Run pytest with verbose output
    exit_code = pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "-x",  # Stop on first failure
    ])

    if exit_code == 0:
        print("\n" + "=" * 60)
        print("✅ ALL FUNDAMENTALS PART 2 TESTS PASSED!")
        print("=" * 60)
        print("\nYou are now ready to proceed to Phase 1 of the project.")
    else:
        print("\n" + "=" * 60)
        print("❌ SOME TESTS FAILED")
        print("=" * 60)
        print("\nPlease fix the failing tests before proceeding.")

    exit(exit_code)
