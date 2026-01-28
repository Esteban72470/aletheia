"""Document data model."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class BoundingBox(BaseModel):
    """Bounding box coordinates."""

    x: float = Field(..., description="X coordinate (left)")
    y: float = Field(..., description="Y coordinate (top)")
    width: float = Field(..., ge=0, description="Width")
    height: float = Field(..., ge=0, description="Height")


class Block(BaseModel):
    """Content block within a page."""

    id: str = Field(..., description="Unique block identifier")
    type: str = Field(
        ...,
        description="Block type: paragraph, heading, list, table, figure, code, equation, caption, footer, header",
    )
    content: str = Field(..., description="Text content of the block")
    bbox: BoundingBox = Field(..., description="Bounding box coordinates")
    confidence: float = Field(
        default=1.0, ge=0.0, le=1.0, description="Confidence score"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional block metadata"
    )


class Page(BaseModel):
    """Single page in a document."""

    page_number: int = Field(..., ge=1, description="Page number (1-indexed)")
    width: float = Field(..., gt=0, description="Page width in points")
    height: float = Field(..., gt=0, description="Page height in points")
    blocks: List[Block] = Field(
        default_factory=list, description="Content blocks on this page"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None, description="Page-level metadata"
    )


class Source(BaseModel):
    """Document source information."""

    filename: str = Field(..., description="Original filename")
    uri: str = Field(..., description="Document URI")
    mime_type: str = Field(..., description="MIME type")
    size_bytes: int = Field(..., ge=0, description="File size in bytes")
    hash: Optional[str] = Field(default=None, description="File hash (e.g., sha256:...)")


class Metadata(BaseModel):
    """Document metadata."""

    title: Optional[str] = Field(default=None, description="Document title")
    author: Optional[str] = Field(default=None, description="Document author")
    creation_date: Optional[datetime] = Field(
        default=None, description="Creation date"
    )
    modification_date: Optional[datetime] = Field(
        default=None, description="Last modification date"
    )
    page_count: int = Field(default=0, ge=0, description="Total number of pages")
    language: Optional[str] = Field(default=None, description="Document language (ISO 639-1)")
    keywords: Optional[List[str]] = Field(
        default=None, description="Document keywords"
    )
    custom: Optional[Dict[str, Any]] = Field(
        default=None, description="Custom metadata fields"
    )


class Provenance(BaseModel):
    """Parsing provenance information."""

    parser_version: str = Field(..., description="Parser version")
    parsed_at: datetime = Field(..., description="Parsing timestamp")
    pipeline_stages: List[str] = Field(
        default_factory=list, description="Pipeline stages executed"
    )
    processing_time_ms: Optional[int] = Field(
        default=None, ge=0, description="Processing time in milliseconds"
    )
    errors: Optional[List[str]] = Field(
        default=None, description="Errors encountered during parsing"
    )
    warnings: Optional[List[str]] = Field(
        default=None, description="Warnings encountered during parsing"
    )


class Document(BaseModel):
    """Parsed document model."""

    document_id: str = Field(..., description="Unique document identifier")
    source: Source = Field(..., description="Source information")
    metadata: Metadata = Field(
        default_factory=Metadata, description="Document metadata"
    )
    pages: List[Page] = Field(
        default_factory=list, description="Document pages"
    )
    provenance: Optional[Provenance] = Field(
        default=None, description="Parsing provenance"
    )
    embeddings: Optional[Dict[str, Any]] = Field(
        default=None, description="Document embeddings for semantic search"
    )
