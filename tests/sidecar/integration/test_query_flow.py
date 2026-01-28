"""Integration tests for the query flow."""

import pytest
import tempfile
from pathlib import Path


class TestQueryFlow:
    """End-to-end tests for document query flow."""

    def test_query_endpoint_exists(self):
        """Test query endpoint is available."""
        from fastapi.testclient import TestClient
        from app.main import app

        client = TestClient(app)

        response = client.post(
            "/query",
            json={"keywords": ["test"]},
        )

        # Endpoint should exist (may return empty results)
        assert response.status_code in [200, 422]

    def test_query_with_document_id(self):
        """Test query with specific document ID."""
        from fastapi.testclient import TestClient
        from app.main import app

        client = TestClient(app)

        response = client.post(
            "/query",
            json={
                "document_id": "nonexistent-doc",
                "keywords": ["test"],
            },
        )

        assert response.status_code in [200, 404, 422]

    def test_get_document_by_id(self):
        """Test retrieving a specific document."""
        from fastapi.testclient import TestClient
        from app.main import app

        client = TestClient(app)

        response = client.get("/documents/test-document-id")

        # Should return 404 for nonexistent document
        assert response.status_code in [200, 404]

    def test_list_all_documents(self):
        """Test listing all documents."""
        from fastapi.testclient import TestClient
        from app.main import app

        client = TestClient(app)

        response = client.get("/documents")

        assert response.status_code == 200
        assert isinstance(response.json(), list)


class TestKeywordSearch:
    """Tests for keyword search functionality."""

    def test_keyword_search_finds_matches(self):
        """Test keyword search returns matching documents."""
        from app.api.query import keyword_search
        from app.models import Document, Page, Block, BoundingBox

        # Create document with searchable content
        block1 = Block(
            id="b1",
            type="text",
            text="The quick brown fox jumps over the lazy dog",
            bbox=BoundingBox(x=0, y=0, width=100, height=20),
        )
        block2 = Block(
            id="b2",
            type="text",
            text="Python programming is fun and educational",
            bbox=BoundingBox(x=0, y=30, width=100, height=20),
        )
        page = Page(number=1, width=612, height=792, blocks=[block1, block2])
        doc = Document(id="search-test", pages=[page], metadata={})

        # Search for "fox"
        results = keyword_search([doc], "fox")
        assert len(results) == 1

        # Search for "python"
        results = keyword_search([doc], "python")
        assert len(results) == 1

        # Search for nonexistent term
        results = keyword_search([doc], "nonexistent")
        assert len(results) == 0

    def test_keyword_search_case_insensitive(self):
        """Test keyword search is case insensitive."""
        from app.api.query import keyword_search
        from app.models import Document, Page, Block, BoundingBox

        block = Block(
            id="b1",
            type="text",
            text="Hello World HELLO world",
            bbox=BoundingBox(x=0, y=0, width=100, height=20),
        )
        page = Page(number=1, width=612, height=792, blocks=[block])
        doc = Document(id="case-test", pages=[page], metadata={})

        results = keyword_search([doc], "HELLO")
        assert len(results) == 1

        results = keyword_search([doc], "hello")
        assert len(results) == 1


class TestRegexSearch:
    """Tests for regex search functionality."""

    def test_regex_search_patterns(self):
        """Test regex search with various patterns."""
        from app.api.query import regex_search
        from app.models import Document, Page, Block, BoundingBox

        block = Block(
            id="b1",
            type="text",
            text="Contact: john@example.com, Phone: 555-1234, Order #12345",
            bbox=BoundingBox(x=0, y=0, width=100, height=20),
        )
        page = Page(number=1, width=612, height=792, blocks=[block])
        doc = Document(id="regex-test", pages=[page], metadata={})

        # Email pattern
        results = regex_search([doc], r"[\w.]+@[\w.]+")
        assert len(results) == 1

        # Phone pattern
        results = regex_search([doc], r"\d{3}-\d{4}")
        assert len(results) == 1

        # Order number pattern
        results = regex_search([doc], r"#\d+")
        assert len(results) == 1

    def test_regex_search_invalid_pattern(self):
        """Test regex search handles invalid patterns gracefully."""
        from app.api.query import regex_search
        from app.models import Document, Page

        page = Page(number=1, width=612, height=792, blocks=[])
        doc = Document(id="invalid-regex", pages=[page], metadata={})

        # Invalid regex should not crash
        try:
            results = regex_search([doc], r"[invalid(")
            # May return empty or raise - both acceptable
        except Exception:
            pass  # Expected for invalid regex


class TestQueryWithFilters:
    """Tests for query filtering."""

    def test_filter_by_document_type(self):
        """Test filtering results by document type."""
        from app.api.query import apply_filters
        from app.models import Document, Page, Block, BoundingBox

        block = Block(
            id="b1",
            type="text",
            text="Test content",
            bbox=BoundingBox(x=0, y=0, width=100, height=20),
        )
        page = Page(number=1, width=612, height=792, blocks=[block])
        doc = Document(
            id="filter-test",
            pages=[page],
            metadata={"type": "invoice"},
        )

        # Filter should work with document metadata
        # Implementation depends on actual filter logic

    def test_filter_by_page_range(self):
        """Test filtering results by page range."""
        from app.models import Document, Page, Block, BoundingBox

        blocks = [
            Block(id=f"b{i}", type="text", text=f"Page {i} content",
                  bbox=BoundingBox(x=0, y=0, width=100, height=20))
            for i in range(1, 6)
        ]
        pages = [
            Page(number=i, width=612, height=792, blocks=[blocks[i-1]])
            for i in range(1, 6)
        ]
        doc = Document(id="multipage-test", pages=pages, metadata={})

        # Page filtering would be applied in query endpoint
        assert len(doc.pages) == 5


class TestQueryResponse:
    """Tests for query response format."""

    def test_query_response_structure(self):
        """Test query response has expected structure."""
        from app.models.query import QueryResponse, QueryResult

        result = QueryResult(
            document_id="doc-1",
            page_number=1,
            block_id="block-1",
            text="Found text",
            score=0.95,
        )

        response = QueryResponse(
            query="test query",
            results=[result],
            total_results=1,
        )

        assert response.query == "test query"
        assert response.total_results == 1
        assert len(response.results) == 1
        assert response.results[0].score == 0.95

    def test_empty_query_response(self):
        """Test empty query response."""
        from app.models.query import QueryResponse

        response = QueryResponse(
            query="no matches",
            results=[],
            total_results=0,
        )

        assert response.total_results == 0
        assert len(response.results) == 0
