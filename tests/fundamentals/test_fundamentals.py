#!/usr/bin/env python3
"""Test script to verify Aletheia fundamentals."""

import sys
from pathlib import Path

print("=" * 60)
print("Aletheia Fundamentals Test")
print("=" * 60)

# Test 1: Import models
print("\n[1/7] Testing data models...")
try:
    from sidecar.app.models import Document, Page, Block, BoundingBox
    from sidecar.app.models import PerceptionQuery, QueryResponse
    from sidecar.app.models import DiagramGraph, Node, Edge
    print("✓ All models imported successfully")
except Exception as e:
    print(f"✗ Model import failed: {e}")
    sys.exit(1)

# Test 2: Test Pydantic validation
print("\n[2/7] Testing Pydantic validation...")
try:
    bbox = BoundingBox(x=10, y=20, width=100, height=50)
    block = Block(
        id="test1",
        type="paragraph",
        content="Test content",
        bbox=bbox,
        confidence=0.95
    )
    print(f"✓ Created block: {block.id}, confidence: {block.confidence}")
except Exception as e:
    print(f"✗ Validation failed: {e}")
    sys.exit(1)

# Test 3: Import pipeline controller
print("\n[3/7] Testing pipeline controller...")
try:
    from sidecar.app.pipeline.controller import PipelineController
    controller = PipelineController()
    print(f"✓ Pipeline controller initialized (version: {controller.version})")
except Exception as e:
    print(f"✗ Pipeline controller failed: {e}")
    sys.exit(1)

# Test 4: Import document store
print("\n[4/7] Testing document store...")
try:
    from sidecar.app.storage.document_store import DocumentStore
    store = DocumentStore()
    print(f"✓ Document store initialized (count: {store.count()})")
except Exception as e:
    print(f"✗ Document store failed: {e}")
    sys.exit(1)

# Test 5: Test FastAPI app
print("\n[5/7] Testing FastAPI app...")
try:
    from sidecar.app.main import app
    print(f"✓ FastAPI app loaded: {app.title}")
except Exception as e:
    print(f"✗ FastAPI app failed: {e}")
    sys.exit(1)

# Test 6: CLI commands
print("\n[6/7] Testing CLI...")
try:
    from cli.aletheia_cli.main import cli
    from cli.aletheia_cli.client.sidecar_client import SidecarClient
    print("✓ CLI commands loaded")
except Exception as e:
    print(f"✗ CLI failed: {e}")
    sys.exit(1)

# Test 7: Create test document
print("\n[7/7] Testing document creation...")
try:
    from datetime import datetime
    from sidecar.app.models import Source, Metadata, Provenance

    source = Source(
        filename="test.pdf",
        uri="file:///test.pdf",
        mime_type="application/pdf",
        size_bytes=1024,
        hash="sha256:test123"
    )

    metadata = Metadata(
        title="Test Document",
        page_count=1
    )

    page = Page(
        page_number=1,
        width=612,
        height=792,
        blocks=[block]
    )

    provenance = Provenance(
        parser_version="0.1.0",
        parsed_at=datetime.utcnow(),
        pipeline_stages=["ingest", "parse"],
        processing_time_ms=100
    )

    document = Document(
        document_id="test-doc-1",
        source=source,
        metadata=metadata,
        pages=[page],
        provenance=provenance
    )

    print(f"✓ Created document: {document.document_id}")
    print(f"  - Pages: {len(document.pages)}")
    print(f"  - Blocks: {len(document.pages[0].blocks)}")
    print(f"  - Processing time: {document.provenance.processing_time_ms}ms")

    # Test storage
    store.save(document)
    retrieved = store.get(document.document_id)
    assert retrieved.document_id == document.document_id
    print(f"✓ Document stored and retrieved successfully")

except Exception as e:
    print(f"✗ Document creation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("✓ All fundamental tests passed!")
print("=" * 60)
print("\nNext steps:")
print("1. Install dependencies: cd sidecar && poetry install")
print("2. Start sidecar: poetry run uvicorn app.main:app --port 8420")
print("3. Test API: curl http://localhost:8420/health")
print("4. Parse document: aletheia parse examples/minimal_demo/sample.pdf")
