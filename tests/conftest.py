"""Pytest configuration and shared fixtures."""

import pytest
import tempfile
from pathlib import Path
from datetime import datetime


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_pdf_content():
    """Create minimal PDF content for testing."""
    # This is a minimal valid PDF that contains "Hello World"
    return b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792]
   /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>
endobj
4 0 obj
<< /Length 44 >>
stream
BT /F1 12 Tf 100 700 Td (Hello World) Tj ET
endstream
endobj
5 0 obj
<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>
endobj
xref
0 6
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
0000000266 00000 n
0000000359 00000 n
trailer
<< /Size 6 /Root 1 0 R >>
startxref
434
%%EOF"""


@pytest.fixture
def sample_image_content():
    """Create a simple PNG image for testing."""
    # Minimal 1x1 white PNG
    return bytes([
        0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,  # PNG signature
        0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52,  # IHDR chunk
        0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,  # 1x1 dimensions
        0x08, 0x02, 0x00, 0x00, 0x00, 0x90, 0x77, 0x53,
        0xDE, 0x00, 0x00, 0x00, 0x0C, 0x49, 0x44, 0x41,  # IDAT chunk
        0x54, 0x08, 0xD7, 0x63, 0xF8, 0xFF, 0xFF, 0xFF,
        0x00, 0x05, 0xFE, 0x02, 0xFE, 0xDC, 0xCC, 0x59,
        0xE7, 0x00, 0x00, 0x00, 0x00, 0x49, 0x45, 0x4E,  # IEND chunk
        0x44, 0xAE, 0x42, 0x60, 0x82,
    ])


@pytest.fixture
def sample_document():
    """Create a sample Document model for testing."""
    from sidecar.app.models import (
        Document, Page, Block, BoundingBox,
        Source, Metadata, Provenance
    )

    bbox = BoundingBox(x=10, y=20, width=100, height=50)
    block = Block(
        id="test_block_1",
        type="paragraph",
        content="This is test content for the document.",
        bbox=bbox,
        confidence=0.95,
    )

    page = Page(
        page_number=1,
        width=612,
        height=792,
        blocks=[block],
    )

    source = Source(
        filename="test.pdf",
        uri="file:///test.pdf",
        mime_type="application/pdf",
        size_bytes=1024,
        hash="sha256:test123abc",
    )

    metadata = Metadata(
        title="Test Document",
        page_count=1,
    )

    provenance = Provenance(
        parser_version="0.1.0",
        parsed_at=datetime.utcnow(),
        pipeline_stages=["ingest", "ocr"],
        processing_time_ms=100,
    )

    return Document(
        document_id="test-doc-123",
        source=source,
        metadata=metadata,
        pages=[page],
        provenance=provenance,
    )


@pytest.fixture
def document_store(temp_dir):
    """Create a document store with temporary directory."""
    from sidecar.app.storage.filesystem import FileSystemDocumentStore
    return FileSystemDocumentStore(base_dir=temp_dir / "documents")


@pytest.fixture
def memory_store():
    """Create an in-memory document store."""
    from sidecar.app.storage.document_store import DocumentStore
    return DocumentStore()
