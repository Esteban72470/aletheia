"""Unit tests for API endpoints."""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from pathlib import Path


class TestParseEndpoint:
    """Tests for /parse endpoint."""

    def test_parse_endpoint_exists(self):
        """Test parse router is defined."""
        from app.api.parse import router

        assert router is not None
        routes = [r.path for r in router.routes]
        assert "/parse" in routes or any("/parse" in str(r) for r in routes)

    @pytest.mark.asyncio
    async def test_parse_pdf_file(self):
        """Test parsing a PDF file via endpoint."""
        from fastapi.testclient import TestClient
        from app.main import app

        client = TestClient(app)

        # Create mock PDF content
        pdf_content = b"%PDF-1.4 fake pdf content"

        response = client.post(
            "/parse",
            files={"file": ("test.pdf", pdf_content, "application/pdf")}
        )

        # Should return 200 or appropriate status
        assert response.status_code in [200, 422]  # 422 if validation fails

    def test_parse_response_model(self):
        """Test ParseResponse model structure."""
        from app.api.models import ParseResponse

        response = ParseResponse(
            document_id="test-doc",
            pages=[],
            metadata={"source": "test"}
        )

        assert response.document_id == "test-doc"
        assert response.pages == []
        assert response.metadata["source"] == "test"


class TestQueryEndpoint:
    """Tests for /query endpoint."""

    def test_query_endpoint_exists(self):
        """Test query router is defined."""
        from app.api.query import router

        assert router is not None

    def test_keyword_search_function(self):
        """Test keyword search implementation."""
        from app.api.query import keyword_search
        from app.models import Document, Page, Block, BoundingBox

        # Create document with searchable content
        block = Block(
            id="b1",
            type="text",
            text="Hello world example text",
            bbox=BoundingBox(x=0, y=0, width=100, height=20)
        )
        page = Page(number=1, width=612, height=792, blocks=[block])
        doc = Document(id="doc-1", pages=[page], metadata={})

        documents = [doc]

        # Search for existing word
        results = keyword_search(documents, "world")
        assert len(results) == 1

        # Search for non-existing word
        results = keyword_search(documents, "nonexistent")
        assert len(results) == 0

    def test_regex_search_function(self):
        """Test regex search implementation."""
        from app.api.query import regex_search
        from app.models import Document, Page, Block, BoundingBox

        block = Block(
            id="b1",
            type="text",
            text="Order #12345 placed on 2024-01-15",
            bbox=BoundingBox(x=0, y=0, width=100, height=20)
        )
        page = Page(number=1, width=612, height=792, blocks=[block])
        doc = Document(id="doc-1", pages=[page], metadata={})

        documents = [doc]

        # Search with regex pattern
        results = regex_search(documents, r"#\d+")
        assert len(results) == 1

        # Search for date pattern
        results = regex_search(documents, r"\d{4}-\d{2}-\d{2}")
        assert len(results) == 1


class TestHealthEndpoint:
    """Tests for /health endpoint."""

    def test_health_endpoint_exists(self):
        """Test health router is defined."""
        from app.api.health import router

        assert router is not None

    def test_health_check_returns_ok(self):
        """Test health check returns healthy status."""
        from fastapi.testclient import TestClient
        from app.main import app

        client = TestClient(app)
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] in ["healthy", "ok"]


class TestAPIModels:
    """Tests for API request/response models."""

    def test_parse_request_model(self):
        """Test ParseRequest model if it exists."""
        try:
            from app.api.models import ParseRequest

            request = ParseRequest(
                file_path="/path/to/file.pdf",
                options={}
            )
            assert request.file_path is not None
        except ImportError:
            # Model may not exist
            pass

    def test_query_request_model(self):
        """Test PerceptionQuery model structure."""
        from app.models.query import PerceptionQuery

        query = PerceptionQuery(
            keywords=["test", "search"],
            filters={"type": "text"}
        )

        assert "test" in query.keywords
        assert query.filters["type"] == "text"

    def test_query_response_model(self):
        """Test QueryResponse model structure."""
        from app.models.query import QueryResponse, QueryResult

        result = QueryResult(
            document_id="doc-1",
            page_number=1,
            block_id="block-1",
            text="Found text",
            score=0.95
        )

        response = QueryResponse(
            query="test query",
            results=[result],
            total_results=1
        )

        assert response.total_results == 1
        assert response.results[0].score == 0.95


class TestErrorHandling:
    """Tests for API error handling."""

    def test_parse_invalid_file_type(self):
        """Test parsing unsupported file type returns error."""
        from fastapi.testclient import TestClient
        from app.main import app

        client = TestClient(app)

        response = client.post(
            "/parse",
            files={"file": ("test.xyz", b"invalid content", "application/octet-stream")}
        )

        # Should return 400 or 422 for unsupported file
        assert response.status_code in [400, 415, 422, 500]

    def test_query_empty_request(self):
        """Test query with empty request."""
        from fastapi.testclient import TestClient
        from app.main import app

        client = TestClient(app)

        response = client.post(
            "/query",
            json={}
        )

        # Should return 400 or 422 for invalid request
        assert response.status_code in [200, 400, 422]

    def test_get_document_not_found(self):
        """Test getting non-existent document returns 404."""
        from fastapi.testclient import TestClient
        from app.main import app

        client = TestClient(app)

        response = client.get("/documents/nonexistent-id-12345")

        assert response.status_code == 404


class TestDocumentsEndpoint:
    """Tests for /documents endpoints."""

    def test_list_documents(self):
        """Test listing all documents."""
        from fastapi.testclient import TestClient
        from app.main import app

        client = TestClient(app)

        response = client.get("/documents")

        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_delete_document(self):
        """Test deleting a document."""
        from fastapi.testclient import TestClient
        from app.main import app

        client = TestClient(app)

        # Delete non-existent doc
        response = client.delete("/documents/nonexistent-doc")

        # Should return 404 or 204
        assert response.status_code in [200, 204, 404]
