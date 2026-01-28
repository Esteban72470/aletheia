"""Query data model."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class PerceptionQuery(BaseModel):
    """Perception query model for semantic document querying."""

    query: str = Field(
        ...,
        description="Natural language query about the document",
        min_length=1,
    )
    document_id: str = Field(..., description="Document ID to query")
    mode: str = Field(
        default="semantic",
        description="Query mode: semantic, keyword, or hybrid",
        pattern="^(semantic|keyword|hybrid)$",
    )
    max_results: int = Field(
        default=5,
        ge=1,
        le=100,
        description="Maximum number of results to return",
    )
    filters: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Filters to apply (e.g., page_number, block_type)",
    )
    include_context: bool = Field(
        default=True,
        description="Include surrounding blocks for context",
    )


class QueryResult(BaseModel):
    """Result from a perception query."""

    block_id: str = Field(..., description="Matched block ID")
    page_number: int = Field(..., ge=1, description="Page number")
    content: str = Field(..., description="Block content")
    score: float = Field(
        ..., ge=0.0, le=1.0, description="Relevance score"
    )
    context_before: Optional[str] = Field(
        default=None, description="Content before matched block"
    )
    context_after: Optional[str] = Field(
        default=None, description="Content after matched block"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional metadata"
    )


class QueryResponse(BaseModel):
    """Response for a perception query."""

    query: str = Field(..., description="Original query")
    document_id: str = Field(..., description="Document ID queried")
    results: List[QueryResult] = Field(
        default_factory=list, description="Query results"
    )
    total_matches: int = Field(
        default=0, ge=0, description="Total number of matches found"
    )
    processing_time_ms: Optional[int] = Field(
        default=None, ge=0, description="Query processing time"
    )
