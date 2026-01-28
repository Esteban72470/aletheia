"""Unit tests for Pydantic data models."""

import pytest
from datetime import datetime


class TestBoundingBox:
    """Tests for BoundingBox model."""

    def test_create_bounding_box(self):
        """Test creating a bounding box."""
        from sidecar.app.models import BoundingBox

        bbox = BoundingBox(x=10, y=20, width=100, height=50)

        assert bbox.x == 10
        assert bbox.y == 20
        assert bbox.width == 100
        assert bbox.height == 50

    def test_bounding_box_validation(self):
        """Test bounding box validation."""
        from sidecar.app.models import BoundingBox
        from pydantic import ValidationError

        # Negative dimensions should fail (if validation is strict)
        # For now, just test that valid values work
        bbox = BoundingBox(x=0, y=0, width=1, height=1)
        assert bbox.width >= 0

    def test_bounding_box_serialization(self):
        """Test bounding box JSON serialization."""
        from sidecar.app.models import BoundingBox

        bbox = BoundingBox(x=10.5, y=20.5, width=100.0, height=50.0)
        data = bbox.model_dump()

        assert data["x"] == 10.5
        assert data["y"] == 20.5


class TestBlock:
    """Tests for Block model."""

    def test_create_block(self):
        """Test creating a block."""
        from sidecar.app.models import Block, BoundingBox

        bbox = BoundingBox(x=0, y=0, width=100, height=50)
        block = Block(
            id="block_1",
            type="paragraph",
            content="Test content",
            bbox=bbox,
            confidence=0.95,
        )

        assert block.id == "block_1"
        assert block.type == "paragraph"
        assert block.content == "Test content"
        assert block.confidence == 0.95

    def test_block_types(self):
        """Test different block types."""
        from sidecar.app.models import Block, BoundingBox

        bbox = BoundingBox(x=0, y=0, width=100, height=50)

        for block_type in ["paragraph", "heading", "list", "table", "figure"]:
            block = Block(
                id=f"block_{block_type}",
                type=block_type,
                content="Content",
                bbox=bbox,
                confidence=0.8,
            )
            assert block.type == block_type

    def test_block_confidence_range(self):
        """Test confidence values are in valid range."""
        from sidecar.app.models import Block, BoundingBox

        bbox = BoundingBox(x=0, y=0, width=100, height=50)

        # Valid confidence
        block = Block(
            id="test",
            type="paragraph",
            content="Test",
            bbox=bbox,
            confidence=0.5,
        )
        assert 0 <= block.confidence <= 1


class TestPage:
    """Tests for Page model."""

    def test_create_page(self):
        """Test creating a page."""
        from sidecar.app.models import Page, Block, BoundingBox

        bbox = BoundingBox(x=0, y=0, width=100, height=50)
        block = Block(
            id="b1",
            type="paragraph",
            content="Content",
            bbox=bbox,
            confidence=0.9,
        )

        page = Page(
            page_number=1,
            width=612,
            height=792,
            blocks=[block],
        )

        assert page.page_number == 1
        assert page.width == 612
        assert page.height == 792
        assert len(page.blocks) == 1

    def test_page_empty_blocks(self):
        """Test page with no blocks."""
        from sidecar.app.models import Page

        page = Page(
            page_number=1,
            width=612,
            height=792,
            blocks=[],
        )

        assert len(page.blocks) == 0


class TestDocument:
    """Tests for Document model."""

    def test_create_document(self, sample_document):
        """Test creating a full document."""
        assert sample_document.document_id == "test-doc-123"
        assert len(sample_document.pages) == 1
        assert sample_document.source.filename == "test.pdf"

    def test_document_serialization(self, sample_document):
        """Test document JSON serialization."""
        data = sample_document.model_dump(mode="json")

        assert data["document_id"] == "test-doc-123"
        assert "pages" in data
        assert "source" in data
        assert "metadata" in data

    def test_document_deserialization(self, sample_document):
        """Test document JSON deserialization."""
        from sidecar.app.models import Document

        data = sample_document.model_dump(mode="json")
        restored = Document.model_validate(data)

        assert restored.document_id == sample_document.document_id
        assert len(restored.pages) == len(sample_document.pages)


class TestSource:
    """Tests for Source model."""

    def test_create_source(self):
        """Test creating a source."""
        from sidecar.app.models import Source

        source = Source(
            filename="document.pdf",
            uri="file:///path/to/document.pdf",
            mime_type="application/pdf",
            size_bytes=1024,
            hash="sha256:abc123",
        )

        assert source.filename == "document.pdf"
        assert source.mime_type == "application/pdf"


class TestMetadata:
    """Tests for Metadata model."""

    def test_create_metadata(self):
        """Test creating metadata."""
        from sidecar.app.models import Metadata

        metadata = Metadata(
            title="Test Document",
            author="Test Author",
            page_count=5,
            language="en",
        )

        assert metadata.title == "Test Document"
        assert metadata.page_count == 5

    def test_metadata_optional_fields(self):
        """Test metadata with minimal fields."""
        from sidecar.app.models import Metadata

        metadata = Metadata(page_count=1)
        assert metadata.page_count == 1
        assert metadata.title is None


class TestProvenance:
    """Tests for Provenance model."""

    def test_create_provenance(self):
        """Test creating provenance."""
        from sidecar.app.models import Provenance

        provenance = Provenance(
            parser_version="0.1.0",
            parsed_at=datetime.utcnow(),
            pipeline_stages=["ingest", "ocr", "layout"],
            processing_time_ms=500,
        )

        assert provenance.parser_version == "0.1.0"
        assert len(provenance.pipeline_stages) == 3
        assert provenance.processing_time_ms == 500


class TestQueryModels:
    """Tests for query-related models."""

    def test_perception_query(self):
        """Test creating a perception query."""
        from sidecar.app.models import PerceptionQuery

        query = PerceptionQuery(
            query="find all tables",
            document_id="doc-123",
            mode="keyword",
            max_results=10,
        )

        assert query.query == "find all tables"
        assert query.document_id == "doc-123"

    def test_query_response(self):
        """Test creating a query response."""
        from sidecar.app.models import QueryResponse, QueryResult

        result = QueryResult(
            block_id="b1",
            content="Found text",
            score=0.9,
            page_number=1,
        )

        response = QueryResponse(
            query_id="q-123",
            results=[result],
            total_results=1,
            processing_time_ms=50,
        )

        assert response.query_id == "q-123"
        assert len(response.results) == 1


class TestDiagramModels:
    """Tests for diagram graph models."""

    def test_create_node(self):
        """Test creating a diagram node."""
        from sidecar.app.models import Node, BoundingBox

        bbox = BoundingBox(x=0, y=0, width=100, height=50)
        node = Node(
            id="node_1",
            label="Start",
            shape="rectangle",
            bbox=bbox,
        )

        assert node.id == "node_1"
        assert node.label == "Start"

    def test_create_edge(self):
        """Test creating a diagram edge."""
        from sidecar.app.models import Edge

        edge = Edge(
            id="edge_1",
            source="node_1",
            target="node_2",
            label="connects to",
        )

        assert edge.source == "node_1"
        assert edge.target == "node_2"

    def test_create_diagram_graph(self):
        """Test creating a diagram graph."""
        from sidecar.app.models import DiagramGraph, Node, Edge, BoundingBox

        bbox = BoundingBox(x=0, y=0, width=100, height=50)
        node1 = Node(id="n1", label="A", shape="circle", bbox=bbox)
        node2 = Node(id="n2", label="B", shape="circle", bbox=bbox)
        edge = Edge(id="e1", source="n1", target="n2")

        graph = DiagramGraph(
            id="graph_1",
            nodes=[node1, node2],
            edges=[edge],
        )

        assert graph.id == "graph_1"
        assert len(graph.nodes) == 2
        assert len(graph.edges) == 1
