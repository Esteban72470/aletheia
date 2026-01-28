"""Parse endpoint for document processing."""

from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.api.models import ParseOptions, ParseResponse
from app.pipeline.orchestrator import PipelineOrchestrator
from app.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()

# Document store will be injected
_document_store = None


def set_document_store(store):
    """Inject the document store dependency."""
    global _document_store
    _document_store = store


@router.post("/parse", response_model=ParseResponse)
async def parse_document(
    file: UploadFile = File(...),
    options: Optional[str] = Form(None),
) -> ParseResponse:
    """
    Parse a document and return structured output.

    Args:
        file: Document file (PDF, image)
        options: JSON string with parsing options

    Returns:
        Parsed document with pages, blocks, tables, etc.
    """
    # Validate file type
    allowed_types = ["application/pdf", "image/png", "image/jpeg", "image/tiff"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file.content_type}",
        )

    # Parse options
    parse_options = ParseOptions.model_validate_json(options) if options else ParseOptions()

    # Read file content
    content = await file.read()

    logger.info(f"Parsing document: {file.filename} ({len(content)} bytes)")

    # Process through pipeline
    orchestrator = PipelineOrchestrator()
    result = await orchestrator.process(
        content=content,
        filename=file.filename or "document",
        content_type=file.content_type,
        options=parse_options,
    )

    # Save to document store if available
    if _document_store is not None:
        try:
            # Convert ParseResponse to Document model for storage
            from app.models import Document, Page, Block, BoundingBox, Source, Metadata, Provenance
            from datetime import datetime

            # Build Document from ParseResponse
            pages = []
            for p in result.pages:
                blocks = []
                for b in p.blocks:
                    blocks.append(Block(
                        id=b.id,
                        type=b.type,
                        content=b.text,
                        bbox=BoundingBox(
                            x=b.bbox[0] if len(b.bbox) >= 4 else 0,
                            y=b.bbox[1] if len(b.bbox) >= 4 else 0,
                            width=b.bbox[2] - b.bbox[0] if len(b.bbox) >= 4 else 0,
                            height=b.bbox[3] - b.bbox[1] if len(b.bbox) >= 4 else 0,
                        ),
                        confidence=b.confidence,
                    ))
                pages.append(Page(
                    page_number=p.page_number,
                    width=p.width,
                    height=p.height,
                    blocks=blocks,
                ))

            document = Document(
                document_id=result.document_id,
                source=Source(
                    filename=file.filename or "document",
                    uri=f"upload://{file.filename}",
                    mime_type=file.content_type,
                    size_bytes=len(content),
                    hash=f"sha256:{result.document_id}",
                ),
                metadata=Metadata(
                    page_count=result.metadata.total_pages,
                ),
                pages=pages,
                provenance=Provenance(
                    parser_version="0.1.0",
                    parsed_at=datetime.utcnow(),
                    pipeline_stages=["ingest", "ocr"],
                    processing_time_ms=result.metadata.processing_time_ms,
                ),
            )
            _document_store.save(document)
            logger.info(f"Document saved: {result.document_id}")
        except Exception as e:
            logger.warning(f"Failed to save document to store: {e}")

    return result
