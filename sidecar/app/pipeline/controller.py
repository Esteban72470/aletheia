"""Pipeline controller for document processing."""

import hashlib
import time
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.models import (
    Block,
    BoundingBox,
    Document,
    Metadata,
    Page,
    Provenance,
    QueryResult,
    Source,
)
from app.models.query import PerceptionQuery


class PipelineController:
    """
    Controls the document processing pipeline.

    Orchestrates the flow through stages:
    1. Ingest - Load and validate document
    2. Preprocess - Normalize and prepare
    3. Layout - Detect structure
    4. OCR - Extract text
    5. Tables - Extract tables (optional)
    6. Figures - Extract figures (optional)
    7. Semantic - Generate embeddings (optional)
    8. Postprocess - Clean and finalize
    """

    def __init__(self):
        """Initialize pipeline controller."""
        self.version = "0.1.0"

    async def process(
        self,
        filename: str,
        content: bytes,
        mime_type: str,
        options: Dict[str, Any],
    ) -> Document:
        """
        Process a document through the pipeline.

        Args:
            filename: Original filename
            content: File content bytes
            mime_type: MIME type
            options: Processing options

        Returns:
            Parsed document
        """
        start_time = time.time()
        document_id = str(uuid.uuid4())

        # Calculate hash
        file_hash = hashlib.sha256(content).hexdigest()

        # Create source
        source = Source(
            filename=filename,
            uri=f"temp://{filename}",
            mime_type=mime_type,
            size_bytes=len(content),
            hash=f"sha256:{file_hash}",
        )

        # Initialize provenance
        pipeline_stages = ["ingest"]

        # Stage 1: Ingest
        try:
            if mime_type == "application/pdf":
                pages = await self._ingest_pdf(content, options)
                pipeline_stages.append("pdf_ingest")
            else:
                pages = await self._ingest_image(content, options)
                pipeline_stages.append("image_ingest")

            # Extract metadata
            metadata = self._extract_metadata(filename, pages)
            pipeline_stages.append("metadata")

            # Stage 2-8: Additional processing stages would go here
            # For now, we have basic ingestion

            # Calculate processing time
            processing_time = int((time.time() - start_time) * 1000)

            # Create provenance
            provenance = Provenance(
                parser_version=self.version,
                parsed_at=datetime.utcnow(),
                pipeline_stages=pipeline_stages,
                processing_time_ms=processing_time,
            )

            # Build document
            document = Document(
                document_id=document_id,
                source=source,
                metadata=metadata,
                pages=pages,
                provenance=provenance,
            )

            return document

        except Exception as e:
            # Create error document
            provenance = Provenance(
                parser_version=self.version,
                parsed_at=datetime.utcnow(),
                pipeline_stages=pipeline_stages,
                processing_time_ms=int((time.time() - start_time) * 1000),
                errors=[str(e)],
            )

            return Document(
                document_id=document_id,
                source=source,
                metadata=Metadata(),
                pages=[],
                provenance=provenance,
            )

    async def _ingest_pdf(
        self, content: bytes, options: Dict[str, Any]
    ) -> List[Page]:
        """
        Ingest PDF document.

        Args:
            content: PDF content
            options: Processing options

        Returns:
            List of pages
        """
        try:
            import fitz  # PyMuPDF

            # Open PDF from bytes
            pdf_document = fitz.open(stream=content, filetype="pdf")
            pages = []

            try:
                for page_num in range(len(pdf_document)):
                    pdf_page = pdf_document[page_num]

                    # Get page dimensions
                    rect = pdf_page.rect
                    width = rect.width
                    height = rect.height

                    # Extract text blocks
                    blocks = []
                    text_blocks = pdf_page.get_text("blocks")

                    for idx, block in enumerate(text_blocks):
                        # Block format: (x0, y0, x1, y1, "text", block_no, block_type)
                        x0, y0, x1, y1, text, block_no, block_type = block

                        if not text or not text.strip():
                            continue

                        blocks.append(
                            Block(
                                id=f"p{page_num + 1}_b{idx}",
                                type="paragraph" if block_type == 0 else "figure",
                                content=text.strip(),
                                bbox=BoundingBox(
                                    x=float(x0),
                                    y=float(y0),
                                    width=float(x1 - x0),
                                    height=float(y1 - y0),
                                ),
                                confidence=1.0,
                            )
                        )

                    pages.append(
                        Page(
                            page_number=page_num + 1,
                            width=width,
                            height=height,
                            blocks=blocks,
                        )
                    )
            finally:
                pdf_document.close()

            return pages

        except ImportError:
            # PyMuPDF not installed, return mock page
            return [
                Page(
                    page_number=1,
                    width=612.0,
                    height=792.0,
                    blocks=[
                        Block(
                            id="b1",
                            type="paragraph",
                            content="[PDF parsing requires PyMuPDF: pip install PyMuPDF]",
                            bbox=BoundingBox(x=72, y=72, width=468, height=648),
                            confidence=0.0,
                        )
                    ],
                )
            ]
        except Exception as e:
            # Error processing PDF
            return [
                Page(
                    page_number=1,
                    width=612.0,
                    height=792.0,
                    blocks=[
                        Block(
                            id="b1",
                            type="paragraph",
                            content=f"[PDF parsing error: {str(e)}]",
                            bbox=BoundingBox(x=72, y=72, width=468, height=648),
                            confidence=0.0,
                        )
                    ],
                )
            ]

    async def _ingest_image(
        self, content: bytes, options: Dict[str, Any]
    ) -> List[Page]:
        """
        Ingest image document.

        Args:
            content: Image content
            options: Processing options

        Returns:
            List of pages (single page for images)
        """
        try:
            from PIL import Image
            import pytesseract
            import io

            # Open image
            image = Image.open(io.BytesIO(content))

            # Convert to RGB if needed
            if image.mode != "RGB":
                image = image.convert("RGB")

            width, height = image.size

            # Perform OCR if enabled
            if options.get("ocr_enabled", True):
                try:
                    # Simple OCR extraction
                    text = pytesseract.image_to_string(image)
                    blocks = [
                        Block(
                            id="b1",
                            type="paragraph",
                            content=text.strip() if text.strip() else "[No text detected]",
                            bbox=BoundingBox(x=0, y=0, width=width, height=height),
                            confidence=0.8,
                        )
                    ]
                except Exception as ocr_error:
                    blocks = [
                        Block(
                            id="b1",
                            type="paragraph",
                            content=f"[OCR error: {str(ocr_error)}]",
                            bbox=BoundingBox(x=0, y=0, width=width, height=height),
                            confidence=0.0,
                        )
                    ]
            else:
                blocks = [
                    Block(
                        id="b1",
                        type="figure",
                        content="[OCR disabled]",
                        bbox=BoundingBox(x=0, y=0, width=width, height=height),
                        confidence=0.0,
                    )
                ]

            return [
                Page(
                    page_number=1,
                    width=float(width),
                    height=float(height),
                    blocks=blocks,
                )
            ]

        except ImportError as import_error:
            # Required libraries not installed
            return [
                Page(
                    page_number=1,
                    width=800.0,
                    height=600.0,
                    blocks=[
                        Block(
                            id="b1",
                            type="paragraph",
                            content=f"[Image OCR requires: {str(import_error)}]",
                            bbox=BoundingBox(x=0, y=0, width=800, height=600),
                            confidence=0.0,
                        )
                    ],
                )
            ]
        except Exception as e:
            # Error processing image
            return [
                Page(
                    page_number=1,
                    width=800.0,
                    height=600.0,
                    blocks=[
                        Block(
                            id="b1",
                            type="paragraph",
                            content=f"[Image processing error: {str(e)}]",
                            bbox=BoundingBox(x=0, y=0, width=800, height=600),
                            confidence=0.0,
                        )
                    ],
                )
            ]

    def _extract_metadata(self, filename: str, pages: List[Page]) -> Metadata:
        """
        Extract metadata from document.

        Args:
            filename: Original filename
            pages: Document pages

        Returns:
            Document metadata
        """
        return Metadata(
            title=filename,
            page_count=len(pages),
            creation_date=datetime.utcnow(),
        )

    async def query(
        self, document: Document, query: PerceptionQuery
    ) -> List[QueryResult]:
        """
        Query a document using perception query.

        Supports keyword matching with relevance scoring based on:
        - Exact match vs partial match
        - Number of keyword occurrences
        - Block type weighting (headings score higher)

        Args:
            document: Document to query
            query: Perception query

        Returns:
            List of query results sorted by relevance score
        """
        import re

        results = []
        query_lower = query.query.lower()
        query_words = query_lower.split()

        for page in document.pages:
            for block in page.blocks:
                content_lower = block.content.lower()

                # Calculate relevance score
                score = 0.0

                # Check for exact phrase match (highest score)
                if query_lower in content_lower:
                    score = 0.9
                else:
                    # Count matching words
                    matches = sum(1 for word in query_words if word in content_lower)
                    if matches > 0:
                        score = 0.5 + (0.3 * matches / len(query_words))

                if score > 0:
                    # Boost score for headings/titles
                    if block.block_type in ("heading", "title"):
                        score = min(1.0, score + 0.1)

                    results.append(
                        QueryResult(
                            block_id=block.id,
                            page_number=page.page_number,
                            content=block.content,
                            score=round(score, 2),
                        )
                    )

        # Sort by score descending and limit results
        results.sort(key=lambda r: r.score, reverse=True)
        return results[:query.max_results]
