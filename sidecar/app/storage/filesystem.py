"""File system utilities and document storage."""

import json
import os
import shutil
import time
from pathlib import Path
from typing import Dict, List, Optional

from app.config import settings
from app.models import Document


class FileSystem:
    """File system operations for document handling."""

    def __init__(self, base_dir: Optional[Path] = None):
        """
        Initialize file system handler.

        Args:
            base_dir: Base directory for operations
        """
        self.base_dir = base_dir or settings.cache_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save_temp(self, content: bytes, filename: str) -> Path:
        """
        Save content to a temporary file.

        Args:
            content: File content
            filename: Original filename

        Returns:
            Path to saved file
        """
        temp_dir = self.base_dir / "temp"
        temp_dir.mkdir(exist_ok=True)

        file_path = temp_dir / filename
        file_path.write_bytes(content)
        return file_path

    def get_temp(self, filename: str) -> Optional[bytes]:
        """
        Get content from a temporary file.

        Args:
            filename: Filename

        Returns:
            File content or None
        """
        file_path = self.base_dir / "temp" / filename
        if file_path.exists():
            return file_path.read_bytes()
        return None

    def delete_temp(self, filename: str) -> bool:
        """
        Delete a temporary file.

        Args:
            filename: Filename

        Returns:
            True if deleted
        """
        file_path = self.base_dir / "temp" / filename
        if file_path.exists():
            file_path.unlink()
            return True
        return False

    def cleanup_temp(self, max_age_hours: int = 24) -> int:
        """
        Cleanup old temporary files.

        Args:
            max_age_hours: Maximum file age in hours

        Returns:
            Number of files deleted
        """
        import time

        temp_dir = self.base_dir / "temp"
        if not temp_dir.exists():
            return 0

        count = 0
        now = time.time()
        max_age_seconds = max_age_hours * 3600

        for file_path in temp_dir.iterdir():
            if file_path.is_file():
                age = now - file_path.stat().st_mtime
                if age > max_age_seconds:
                    file_path.unlink()
                    count += 1

        return count

    def list_temp(self) -> List[str]:
        """
        List temporary files.

        Returns:
            List of filenames
        """
        temp_dir = self.base_dir / "temp"
        if not temp_dir.exists():
            return []
        return [f.name for f in temp_dir.iterdir() if f.is_file()]

    def get_size(self) -> int:
        """
        Get total cache size in bytes.

        Returns:
            Total size in bytes
        """
        total = 0
        for path in self.base_dir.rglob("*"):
            if path.is_file():
                total += path.stat().st_size
        return total


class FileSystemDocumentStore:
    """
    Persistent document storage using the file system.

    Stores documents as JSON files for durability across restarts.
    Uses an in-memory cache for fast access.
    """

    def __init__(self, base_dir: Optional[Path] = None):
        """
        Initialize file system document store.

        Args:
            base_dir: Base directory for document storage
        """
        self.base_dir = base_dir or (settings.cache_dir / "documents")
        self.base_dir.mkdir(parents=True, exist_ok=True)

        # In-memory cache
        self._cache: Dict[str, Document] = {}
        self._cache_loaded = False

    def _get_document_path(self, document_id: str) -> Path:
        """Get the file path for a document."""
        return self.base_dir / f"{document_id}.json"

    def _load_cache(self) -> None:
        """Load all documents into memory cache."""
        if self._cache_loaded:
            return

        for file_path in self.base_dir.glob("*.json"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    document = Document.model_validate(data)
                    self._cache[document.document_id] = document
            except Exception as e:
                # Log but don't fail on corrupt files
                print(f"Warning: Failed to load {file_path}: {e}")

        self._cache_loaded = True

    def save(self, document: Document) -> None:
        """
        Save a document to disk and cache.

        Args:
            document: Document to save
        """
        # Save to disk atomically
        file_path = self._get_document_path(document.document_id)
        temp_path = file_path.with_suffix(".tmp")

        try:
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(document.model_dump(mode="json"), f, indent=2, default=str)

            # Atomic rename
            temp_path.replace(file_path)

            # Update cache
            self._cache[document.document_id] = document

        except Exception as e:
            # Clean up temp file on error
            if temp_path.exists():
                temp_path.unlink()
            raise e

    def get(self, document_id: str) -> Optional[Document]:
        """
        Retrieve a document by ID.

        Args:
            document_id: Document identifier

        Returns:
            Document if found, None otherwise
        """
        # Check cache first
        if document_id in self._cache:
            return self._cache[document_id]

        # Try loading from disk
        file_path = self._get_document_path(document_id)
        if file_path.exists():
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    document = Document.model_validate(data)
                    self._cache[document_id] = document
                    return document
            except Exception:
                return None

        return None

    def delete(self, document_id: str) -> bool:
        """
        Delete a document by ID.

        Args:
            document_id: Document identifier

        Returns:
            True if deleted, False if not found
        """
        # Remove from cache
        if document_id in self._cache:
            del self._cache[document_id]

        # Remove from disk
        file_path = self._get_document_path(document_id)
        if file_path.exists():
            file_path.unlink()
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
        self._load_cache()

        docs = list(self._cache.values())
        return [
            {
                "document_id": doc.document_id,
                "filename": doc.source.filename if doc.source else "unknown",
                "page_count": doc.metadata.page_count if doc.metadata else 0,
                "parsed_at": doc.provenance.parsed_at if doc.provenance else None,
            }
            for doc in docs[offset : offset + limit]
        ]

    def clear(self) -> None:
        """Clear all documents from disk and cache."""
        self._cache.clear()

        for file_path in self.base_dir.glob("*.json"):
            file_path.unlink()

    def count(self) -> int:
        """Get total number of stored documents."""
        self._load_cache()
        return len(self._cache)

    def exists(self, document_id: str) -> bool:
        """Check if a document exists."""
        if document_id in self._cache:
            return True
        return self._get_document_path(document_id).exists()
