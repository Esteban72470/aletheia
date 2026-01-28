"""Query endpoint for perception queries."""

import re
from typing import List, Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException

from app.api.models import PerceptionQuery, QueryResponse, QueryResult
from app.logging import get_logger
from app.models import Document

logger = get_logger(__name__)

router = APIRouter()

# Document store will be injected
_document_store = None


def set_document_store(store):
    """Inject the document store dependency."""
    global _document_store
    _document_store = store


def get_document_store():
    """Get the document store."""
    if _document_store is None:
        raise HTTPException(status_code=500, detail="Document store not initialized")
    return _document_store


@router.post("/query", response_model=QueryResponse)
async def query_document(query: PerceptionQuery) -> QueryResponse:
    """
    Query a parsed document.

    Args:
        query: Perception query with document_id and query parameters

    Returns:
        Query results with extracted information
    """
    if not query.document_id:
        raise HTTPException(status_code=400, detail="document_id is required")

    store = get_document_store()

    # Get document from store
    document = store.get(query.document_id)
    if not document:
        raise HTTPException(
            status_code=404,
            detail=f"Document not found: {query.document_id}"
        )

    logger.info(f"Querying document {query.document_id}: {query.query}")

    # Execute query based on mode
    mode = query.options.get("mode", "keyword") if query.options else "keyword"
    results = []

    if query.query:
        if mode == "keyword":
            results = keyword_search(document, query.query, query.page_range)
        elif mode == "regex":
            results = regex_search(document, query.query, query.page_range)
        else:
            # Default to keyword search
            results = keyword_search(document, query.query, query.page_range)

    # Apply filters
    if query.filters:
        results = apply_filters(results, query.filters)

    # Limit results
    max_results = query.options.get("max_results", 10) if query.options else 10
    results = results[:max_results]

    # Calculate overall confidence
    overall_confidence = 0.0
    if results:
        overall_confidence = sum(r.confidence for r in results) / len(results)

    return QueryResponse(
        query_id=str(uuid4())[:8],
        results=results,
        confidence=overall_confidence,
    )


def keyword_search(
    document: Document,
    query_text: str,
    page_range: Optional[List[int]] = None
) -> List[QueryResult]:
    """
    Perform keyword search on document blocks.

    Args:
        document: Document to search
        query_text: Search query
        page_range: Optional list of page numbers to search

    Returns:
        List of matching results
    """
    results = []
    query_lower = query_text.lower()
    keywords = query_lower.split()

    for page in document.pages:
        # Check page range filter
        if page_range and page.page_number not in page_range:
            continue

        for block in page.blocks:
            text_lower = block.content.lower() if block.content else ""

            # Check if any keyword matches
            matches = sum(1 for kw in keywords if kw in text_lower)
            if matches > 0:
                # Calculate relevance score based on match percentage
                relevance = matches / len(keywords)

                results.append(
                    QueryResult(
                        extraction_id=f"{document.document_id}_{block.id}",
                        type=block.type,
                        value=block.content,
                        confidence=relevance * block.confidence,
                        location={
                            "page": page.page_number,
                            "block_id": block.id,
                            "bbox": [block.bbox.x, block.bbox.y,
                                     block.bbox.x + block.bbox.width,
                                     block.bbox.y + block.bbox.height]
                            if block.bbox else None,
                        },
                    )
                )

    # Sort by confidence
    results.sort(key=lambda r: r.confidence, reverse=True)
    return results


def regex_search(
    document: Document,
    pattern: str,
    page_range: Optional[List[int]] = None
) -> List[QueryResult]:
    """
    Perform regex search on document blocks.

    Args:
        document: Document to search
        pattern: Regex pattern
        page_range: Optional list of page numbers to search

    Returns:
        List of matching results
    """
    results = []

    try:
        regex = re.compile(pattern, re.IGNORECASE)
    except re.error as e:
        logger.warning(f"Invalid regex pattern: {e}")
        return []

    for page in document.pages:
        # Check page range filter
        if page_range and page.page_number not in page_range:
            continue

        for block in page.blocks:
            text = block.content or ""
            matches = list(regex.finditer(text))

            for match in matches:
                results.append(
                    QueryResult(
                        extraction_id=f"{document.document_id}_{block.id}_{match.start()}",
                        type="match",
                        value=match.group(),
                        confidence=block.confidence,
                        location={
                            "page": page.page_number,
                            "block_id": block.id,
                            "match_start": match.start(),
                            "match_end": match.end(),
                            "context": text[max(0, match.start() - 50):match.end() + 50],
                        },
                    )
                )

    return results


def apply_filters(
    results: List[QueryResult],
    filters: dict
) -> List[QueryResult]:
    """
    Apply filters to query results.

    Args:
        results: List of results to filter
        filters: Filter criteria

    Returns:
        Filtered results
    """
    filtered = results

    # Filter by type
    if "types" in filters:
        allowed_types = filters["types"]
        filtered = [r for r in filtered if r.type in allowed_types]

    # Filter by minimum confidence
    if "min_confidence" in filters:
        min_conf = filters["min_confidence"]
        filtered = [r for r in filtered if r.confidence >= min_conf]

    # Filter by page
    if "pages" in filters:
        allowed_pages = filters["pages"]
        filtered = [
            r for r in filtered
            if r.location and r.location.get("page") in allowed_pages
        ]

    return filtered


@router.get("/documents/{document_id}")
async def get_document(document_id: str):
    """
    Get a parsed document by ID.

    Args:
        document_id: Document identifier

    Returns:
        The parsed document
    """
    store = get_document_store()
    document = store.get(document_id)

    if not document:
        raise HTTPException(
            status_code=404,
            detail=f"Document not found: {document_id}"
        )

    return document.model_dump(mode="json")


@router.get("/documents")
async def list_documents(limit: int = 100, offset: int = 0):
    """
    List all parsed documents.

    Args:
        limit: Maximum number of documents to return
        offset: Number of documents to skip

    Returns:
        List of document metadata
    """
    store = get_document_store()
    return {
        "documents": store.list(limit=limit, offset=offset),
        "total": store.count(),
    }


@router.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """
    Delete a parsed document.

    Args:
        document_id: Document identifier

    Returns:
        Deletion confirmation
    """
    store = get_document_store()

    if not store.get(document_id):
        raise HTTPException(
            status_code=404,
            detail=f"Document not found: {document_id}"
        )

    store.delete(document_id)
    return {"deleted": document_id}
