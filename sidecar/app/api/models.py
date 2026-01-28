"""Pydantic models for API requests and responses."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# --- Parse Models ---


class ParseOptions(BaseModel):
    """Options for document parsing."""

    pages: Optional[str] = Field(None, description="Page range, e.g., '1-5' or '1,3,5'")
    ocr_engine: str = Field("tesseract", description="OCR engine to use")
    extract_tables: bool = Field(True, description="Extract tables")
    extract_layout: bool = Field(True, description="Detect layout blocks")
    output_level: str = Field("L1", description="Output abstraction level (L0-L3)")


class BoundingBox(BaseModel):
    """Bounding box coordinates [x1, y1, x2, y2]."""

    x1: float
    y1: float
    x2: float
    y2: float

    def as_list(self) -> List[float]:
        return [self.x1, self.y1, self.x2, self.y2]


class Block(BaseModel):
    """A text block in a document."""

    id: str
    type: str = Field(..., description="Block type: paragraph, heading, list, etc.")
    bbox: List[float] = Field(..., description="[x1, y1, x2, y2]")
    text: str = ""
    confidence: float = Field(0.0, ge=0.0, le=1.0)


class Table(BaseModel):
    """An extracted table."""

    id: str
    bbox: List[float]
    rows: int
    columns: int
    cells: List[List[str]] = []
    csv: Optional[str] = None


class Figure(BaseModel):
    """An extracted figure/image."""

    id: str
    bbox: List[float]
    caption: Optional[str] = None
    figure_type: Optional[str] = None


class Page(BaseModel):
    """A parsed page."""

    page_number: int
    width: float
    height: float
    blocks: List[Block] = []
    tables: List[Table] = []
    figures: List[Figure] = []


class DocumentMetadata(BaseModel):
    """Document parsing metadata."""

    total_pages: int
    processing_time_ms: int
    ocr_engine: Optional[str] = None
    layout_model: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ParseResponse(BaseModel):
    """Response from parse endpoint."""

    document_id: str
    pages: List[Page]
    metadata: DocumentMetadata


# --- Query Models ---


class PerceptionQuery(BaseModel):
    """Query for extracting information from parsed documents."""

    document_id: str
    query: Optional[str] = None
    page_range: Optional[List[int]] = None
    region: Optional[List[float]] = None
    output_format: str = "structured"
    filters: Optional[Dict[str, Any]] = None
    options: Optional[Dict[str, Any]] = None


class QueryResult(BaseModel):
    """A single query result."""

    extraction_id: str
    type: str
    value: Any
    confidence: float
    location: Optional[Dict[str, Any]] = None


class QueryResponse(BaseModel):
    """Response from query endpoint."""

    query_id: str
    results: List[QueryResult]
    confidence: float
