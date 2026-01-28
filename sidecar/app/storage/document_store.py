"""Document storage implementation."""

from typing import Dict, List, Optional

from app.models import Document


class DocumentStore:
    """
    In-memory document storage.

    Stores parsed documents for retrieval and querying.
    For production, this should be replaced with a proper
    database (e.g., PostgreSQL, MongoDB).
    """

    def __init__(self):
        """Initialize document store."""
        self._documents: Dict[str, Document] = {}

    def save(self, document: Document) -> None:
        """
        Save a document.

        Args:
            document: Document to save
        """
        self._documents[document.document_id] = document

    def get(self, document_id: str) -> Optional[Document]:
        """
        Retrieve a document by ID.

        Args:
            document_id: Document identifier

        Returns:
            Document if found, None otherwise
        """
        return self._documents.get(document_id)

    def delete(self, document_id: str) -> bool:
        """
        Delete a document by ID.

        Args:
            document_id: Document identifier

        Returns:
            True if deleted, False if not found
        """
        if document_id in self._documents:
            del self._documents[document_id]
            return True
        return False

    def list(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """
        List all documents (metadata only).

        Args:
            limit: Maximum number of documents
            offset: Number to skip

        Returns:
            List of document metadata
        """
        docs = list(self._documents.values())
        return [
            {
                "document_id": doc.document_id,
                "filename": doc.source.filename,
                "page_count": doc.metadata.page_count,
                "parsed_at": doc.provenance.parsed_at if doc.provenance else None,
            }
            for doc in docs[offset : offset + limit]
        ]

    def clear(self) -> None:
        """Clear all documents."""
        self._documents.clear()

    def count(self) -> int:
        """Get total number of stored documents."""
        return len(self._documents)
