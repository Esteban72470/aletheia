"""Pipeline orchestrator for coordinating processing stages."""

import hashlib
import logging
import time
from typing import List, Optional
from uuid import uuid4

from app.api.models import (
    Block,
    DocumentMetadata,
    Figure,
    Page,
    ParseOptions,
    ParseResponse,
    Table,
)
from app.logging import get_logger
from app.pipeline.ingest.pdf_loader import PDFLoader
from app.pipeline.ingest.image_loader import ImageLoader
from app.pipeline.ingest.base import LoadedPage
from app.pipeline.ocr.tesseract_backend import TesseractBackend
from app.pipeline.ocr.ocr_base import OCRResult
from app.pipeline.layout import LayoutParserBackend, LayoutBlock

logger = get_logger(__name__)


class PipelineOrchestrator:
    """Orchestrates the document processing pipeline."""

    def __init__(self):
        """Initialize the orchestrator."""
        self.pdf_loader = PDFLoader()
        self.image_loader = ImageLoader()
        self.ocr_backend = None  # Lazy initialized
        self.layout_backend = None  # Lazy initialized
        self._ocr_available = None
        self._layout_available = None

    def _get_layout_backend(self) -> Optional[LayoutParserBackend]:
        """Get layout detection backend, lazily initialized."""
        if self._layout_available is None:
            try:
                self.layout_backend = LayoutParserBackend(use_fallback=True)
                self._layout_available = True
                logger.info("Layout detection backend initialized")
            except Exception as e:
                self._layout_available = False
                logger.warning(f"Layout backend not available: {e}")

        return self.layout_backend if self._layout_available else None

    def _get_ocr_backend(self, engine: str = "tesseract") -> Optional[TesseractBackend]:
        """Get OCR backend, lazily initialized."""
        if self._ocr_available is None:
            try:
                import pytesseract
                pytesseract.get_tesseract_version()
                self._ocr_available = True
            except Exception:
                self._ocr_available = False
                logger.warning("Tesseract not available, OCR will be skipped")

        if self._ocr_available and self.ocr_backend is None:
            self.ocr_backend = TesseractBackend()

        return self.ocr_backend if self._ocr_available else None

    def _get_loader(self, content_type: str):
        """Get appropriate loader for content type."""
        if self.pdf_loader.can_handle(content_type):
            return self.pdf_loader
        elif self.image_loader.can_handle(content_type):
            return self.image_loader
        return None

    async def process(
        self,
        content: bytes,
        filename: str,
        content_type: str,
        options: ParseOptions,
    ) -> ParseResponse:
        """
        Process a document through the pipeline.

        Args:
            content: Raw file content
            filename: Original filename
            content_type: MIME type
            options: Processing options

        Returns:
            Parsed document response
        """
        start_time = time.time()

        # Generate document ID from content hash
        document_id = self._generate_document_id(content)

        logger.info(f"Processing document: {filename} ({document_id})")

        try:
            # Stage 1: Ingest - Load document pages
            loader = self._get_loader(content_type)
            if not loader:
                raise ValueError(f"Unsupported content type: {content_type}")

            loaded_pages = loader.load(content, options.pages)
            logger.info(f"Loaded {len(loaded_pages)} pages")

            # Stage 2-6: Process each page
            pages = []
            for loaded_page in loaded_pages:
                page = await self._process_page(loaded_page, options)
                pages.append(page)

            processing_time = int((time.time() - start_time) * 1000)

            return ParseResponse(
                document_id=document_id,
                pages=pages,
                metadata=DocumentMetadata(
                    total_pages=len(pages),
                    processing_time_ms=processing_time,
                    ocr_engine=options.ocr_engine if self._ocr_available else None,
                    layout_model="basic" if options.extract_layout else None,
                ),
            )

        except Exception as e:
            logger.error(f"Pipeline error: {e}")
            processing_time = int((time.time() - start_time) * 1000)

            return ParseResponse(
                document_id=document_id,
                pages=[],
                metadata=DocumentMetadata(
                    total_pages=0,
                    processing_time_ms=processing_time,
                    ocr_engine=None,
                ),
            )

    async def _process_page(
        self, loaded_page: LoadedPage, options: ParseOptions
    ) -> Page:
        """
        Process a single loaded page through extraction stages.

        Pipeline stages:
        1. Layout detection (optional) - identify regions
        2. Text extraction - OCR or embedded text
        3. Block creation - combine layout and text

        Args:
            loaded_page: Page with image data
            options: Processing options

        Returns:
            Processed page with blocks
        """
        blocks: List[Block] = []
        tables: List[Table] = []
        figures: List[Figure] = []

        # Stage 1: Layout Detection (if enabled)
        layout_blocks: List[LayoutBlock] = []
        layout_model_used = None

        if options.extract_layout:
            layout_backend = self._get_layout_backend()
            if layout_backend and loaded_page.image:
                try:
                    layout_blocks = layout_backend.detect(loaded_page.image)
                    layout_blocks = layout_backend.get_reading_order(layout_blocks)
                    layout_model_used = "layoutparser" if layout_backend.is_available else "heuristic"
                    logger.debug(f"Layout detected {len(layout_blocks)} blocks using {layout_model_used}")
                except Exception as e:
                    logger.warning(f"Layout detection failed for page {loaded_page.page_number}: {e}")

        # Stage 2: Text Extraction
        if loaded_page.text_layer:
            # Use embedded text directly
            if layout_blocks:
                # Combine layout regions with embedded text
                blocks = self._assign_text_to_layout_blocks(
                    loaded_page.page_number,
                    layout_blocks,
                    loaded_page.text_layer,
                    loaded_page.width,
                    loaded_page.height,
                )
            else:
                # No layout info, create single block
                blocks.append(
                    Block(
                        id=f"p{loaded_page.page_number}_b1",
                        type="paragraph",
                        bbox=[0, 0, loaded_page.width, loaded_page.height],
                        text=loaded_page.text_layer.strip(),
                        confidence=1.0,
                    )
                )
        else:
            # Need OCR for image-based content
            ocr_backend = self._get_ocr_backend(options.ocr_engine)
            if ocr_backend:
                try:
                    ocr_result = ocr_backend.recognize(loaded_page.image)

                    if layout_blocks and ocr_result.word_boxes:
                        # Combine layout with OCR word boxes
                        blocks = self._assign_words_to_layout_blocks(
                            loaded_page.page_number,
                            layout_blocks,
                            ocr_result.word_boxes,
                        )
                    elif ocr_result.word_boxes:
                        # Use word boxes to create blocks
                        blocks = self._create_blocks_from_word_boxes(
                            loaded_page.page_number,
                            ocr_result.word_boxes,
                        )
                    elif ocr_result.text.strip():
                        # Fallback: single block with full text
                        blocks.append(
                            Block(
                                id=f"p{loaded_page.page_number}_b1",
                                type="paragraph",
                                bbox=[0, 0, loaded_page.width, loaded_page.height],
                                text=ocr_result.text.strip(),
                                confidence=ocr_result.confidence,
                            )
                        )
                except Exception as e:
                    logger.warning(f"OCR failed for page {loaded_page.page_number}: {e}")

        # Stage 3: Extract tables and figures from layout
        if layout_blocks:
            for lb in layout_blocks:
                if lb.type == "table":
                    tables.append(Table(
                        id=lb.id,
                        bbox=lb.bbox,
                        confidence=lb.confidence,
                        rows=[],  # Table extraction in Phase 1 Part 2
                        headers=[],
                    ))
                elif lb.type == "figure":
                    figures.append(Figure(
                        id=lb.id,
                        bbox=lb.bbox,
                        confidence=lb.confidence,
                        caption="",  # Caption extraction TODO
                    ))

        return Page(
            page_number=loaded_page.page_number,
            width=loaded_page.width,
            height=loaded_page.height,
            blocks=blocks,
            tables=tables,
            figures=figures,
        )

    def _assign_text_to_layout_blocks(
        self,
        page_number: int,
        layout_blocks: List[LayoutBlock],
        full_text: str,
        page_width: float,
        page_height: float,
    ) -> List[Block]:
        """
        Assign embedded text to layout blocks based on position.

        Since embedded text doesn't have word-level positions,
        we distribute text proportionally to block areas.
        """
        if not layout_blocks:
            return [Block(
                id=f"p{page_number}_b1",
                type="paragraph",
                bbox=[0, 0, page_width, page_height],
                text=full_text.strip(),
                confidence=1.0,
            )]

        # For now, assign all text to first text-type block
        # More sophisticated splitting would require text-to-region matching
        blocks = []
        text_assigned = False

        for idx, lb in enumerate(layout_blocks):
            block_text = ""
            if lb.type in ("paragraph", "heading", "list") and not text_assigned:
                block_text = full_text.strip()
                text_assigned = True

            blocks.append(Block(
                id=f"p{page_number}_b{idx + 1}",
                type=lb.type,
                bbox=lb.bbox,
                text=block_text,
                confidence=lb.confidence,
            ))

        return blocks

    def _assign_words_to_layout_blocks(
        self,
        page_number: int,
        layout_blocks: List[LayoutBlock],
        word_boxes: List[dict],
    ) -> List[Block]:
        """
        Assign OCR word boxes to layout blocks based on spatial overlap.
        """
        blocks = []
        assigned_words = set()

        for idx, lb in enumerate(layout_blocks):
            block_words = []

            for word_idx, word in enumerate(word_boxes):
                if word_idx in assigned_words:
                    continue

                # Check if word center is inside layout block
                word_cx = word.get("x", 0) + word.get("width", 0) / 2
                word_cy = word.get("y", 0) + word.get("height", 0) / 2

                if (lb.bbox[0] <= word_cx <= lb.bbox[2] and
                    lb.bbox[1] <= word_cy <= lb.bbox[3]):
                    block_words.append(word)
                    assigned_words.add(word_idx)

            # Sort words in reading order (top-to-bottom, left-to-right)
            block_words.sort(key=lambda w: (w.get("y", 0), w.get("x", 0)))

            # Combine text
            text = " ".join(w.get("text", "") for w in block_words if w.get("text"))

            # Average confidence
            if block_words:
                confs = [w.get("confidence", 0.5) for w in block_words]
                avg_conf = sum(confs) / len(confs)
            else:
                avg_conf = lb.confidence

            blocks.append(Block(
                id=f"p{page_number}_b{idx + 1}",
                type=lb.type,
                bbox=lb.bbox,
                text=text,
                confidence=avg_conf,
            ))

        # Handle any unassigned words
        unassigned = [w for i, w in enumerate(word_boxes) if i not in assigned_words]
        if unassigned:
            unassigned.sort(key=lambda w: (w.get("y", 0), w.get("x", 0)))
            text = " ".join(w.get("text", "") for w in unassigned if w.get("text"))
            if text:
                blocks.append(Block(
                    id=f"p{page_number}_b{len(blocks) + 1}",
                    type="paragraph",
                    bbox=[
                        min(w.get("x", 0) for w in unassigned),
                        min(w.get("y", 0) for w in unassigned),
                        max(w.get("x", 0) + w.get("width", 0) for w in unassigned),
                        max(w.get("y", 0) + w.get("height", 0) for w in unassigned),
                    ],
                    text=text,
                    confidence=0.5,
                ))

        return blocks

    def _create_blocks_from_word_boxes(
        self, page_number: int, word_boxes: List[dict]
    ) -> List[Block]:
        """
        Create text blocks from individual word boxes by grouping nearby words.

        Args:
            page_number: Current page number
            word_boxes: List of word boxes with text and coordinates

        Returns:
            List of grouped text blocks
        """
        if not word_boxes:
            return []

        # Simple line-based grouping
        # Group words that are on the same line (similar y-coordinate)
        lines = []
        current_line = []
        current_line_y = None
        line_threshold = 10  # Pixels

        sorted_boxes = sorted(word_boxes, key=lambda w: (w.get("y", 0), w.get("x", 0)))

        for word in sorted_boxes:
            y = word.get("y", 0)
            if current_line_y is None:
                current_line_y = y
                current_line.append(word)
            elif abs(y - current_line_y) < line_threshold:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(current_line)
                current_line = [word]
                current_line_y = y

        if current_line:
            lines.append(current_line)

        # Convert lines to blocks
        blocks = []
        for idx, line in enumerate(lines):
            if not line:
                continue

            # Calculate bounding box for the line
            x1 = min(w.get("x", 0) for w in line)
            y1 = min(w.get("y", 0) for w in line)
            x2 = max(w.get("x", 0) + w.get("width", 0) for w in line)
            y2 = max(w.get("y", 0) + w.get("height", 0) for w in line)

            # Combine text
            text = " ".join(w.get("text", "") for w in line if w.get("text"))

            # Average confidence
            confidences = [w.get("confidence", 0.5) for w in line]
            avg_conf = sum(confidences) / len(confidences) if confidences else 0.5

            blocks.append(
                Block(
                    id=f"p{page_number}_b{idx + 1}",
                    type="paragraph",
                    bbox=[x1, y1, x2, y2],
                    text=text,
                    confidence=avg_conf,
                )
            )

        return blocks

    def _generate_document_id(self, content: bytes) -> str:
        """Generate a unique document ID from content hash."""
        return hashlib.sha256(content).hexdigest()[:16]
