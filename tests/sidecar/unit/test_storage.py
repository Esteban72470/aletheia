"""Unit tests for storage components."""

import json
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch


class TestDocumentStore:
    """Tests for in-memory DocumentStore."""

    def test_store_initialization(self):
        """Test document store initializes empty."""
        from app.storage import DocumentStore

        store = DocumentStore()
        assert len(store.list_all()) == 0

    def test_save_document(self, sample_document):
        """Test saving a document to store."""
        from app.storage import DocumentStore

        store = DocumentStore()
        store.save(sample_document)

        assert len(store.list_all()) == 1
        assert store.get(sample_document.id) == sample_document

    def test_get_document_not_found(self):
        """Test getting non-existent document returns None."""
        from app.storage import DocumentStore

        store = DocumentStore()
        result = store.get("nonexistent-id")

        assert result is None

    def test_delete_document(self, sample_document):
        """Test deleting a document from store."""
        from app.storage import DocumentStore

        store = DocumentStore()
        store.save(sample_document)

        assert store.delete(sample_document.id) is True
        assert store.get(sample_document.id) is None

    def test_delete_nonexistent_document(self):
        """Test deleting non-existent document returns False."""
        from app.storage import DocumentStore

        store = DocumentStore()
        result = store.delete("nonexistent-id")

        assert result is False

    def test_list_all_documents(self, sample_document):
        """Test listing all documents."""
        from app.storage import DocumentStore
        from app.models import Document, Page

        store = DocumentStore()

        # Create second document
        doc2 = Document(
            id="doc-2",
            pages=[Page(number=1, width=612, height=792, blocks=[])],
            metadata={}
        )

        store.save(sample_document)
        store.save(doc2)

        all_docs = store.list_all()
        assert len(all_docs) == 2

    def test_update_existing_document(self, sample_document):
        """Test updating an existing document."""
        from app.storage import DocumentStore

        store = DocumentStore()
        store.save(sample_document)

        # Modify document
        sample_document.metadata["updated"] = True
        store.save(sample_document)

        retrieved = store.get(sample_document.id)
        assert retrieved.metadata.get("updated") is True
        assert len(store.list_all()) == 1


class TestFileSystemDocumentStore:
    """Tests for file-based FileSystemDocumentStore."""

    def test_store_initialization_creates_directory(self, temp_dir):
        """Test store creates storage directory on init."""
        from app.storage.filesystem import FileSystemDocumentStore

        storage_path = temp_dir / "documents"
        store = FileSystemDocumentStore(base_path=storage_path)

        assert storage_path.exists()

    def test_save_and_load_document(self, temp_dir, sample_document):
        """Test saving and loading document from filesystem."""
        from app.storage.filesystem import FileSystemDocumentStore

        storage_path = temp_dir / "documents"
        store = FileSystemDocumentStore(base_path=storage_path)

        store.save(sample_document)

        # Verify file exists
        doc_file = storage_path / f"{sample_document.id}.json"
        assert doc_file.exists()

        # Load document
        loaded = store.get(sample_document.id)
        assert loaded is not None
        assert loaded.id == sample_document.id

    def test_get_from_cache(self, temp_dir, sample_document):
        """Test document is cached in memory after save."""
        from app.storage.filesystem import FileSystemDocumentStore

        storage_path = temp_dir / "documents"
        store = FileSystemDocumentStore(base_path=storage_path)

        store.save(sample_document)

        # Clear and reload from disk
        store._cache.clear()
        loaded = store.get(sample_document.id)

        # Second get should use cache
        store._cache[sample_document.id] = sample_document
        cached = store.get(sample_document.id)

        assert cached == loaded

    def test_delete_removes_file_and_cache(self, temp_dir, sample_document):
        """Test delete removes both file and cache entry."""
        from app.storage.filesystem import FileSystemDocumentStore

        storage_path = temp_dir / "documents"
        store = FileSystemDocumentStore(base_path=storage_path)

        store.save(sample_document)
        doc_file = storage_path / f"{sample_document.id}.json"

        assert doc_file.exists()

        store.delete(sample_document.id)

        assert not doc_file.exists()
        assert store.get(sample_document.id) is None

    def test_list_all_from_filesystem(self, temp_dir, sample_document):
        """Test list_all scans filesystem for documents."""
        from app.storage.filesystem import FileSystemDocumentStore
        from app.models import Document, Page

        storage_path = temp_dir / "documents"
        store = FileSystemDocumentStore(base_path=storage_path)

        # Save multiple documents
        store.save(sample_document)

        doc2 = Document(
            id="doc-2",
            pages=[Page(number=1, width=612, height=792, blocks=[])],
            metadata={}
        )
        store.save(doc2)

        # Clear cache to force filesystem scan
        store._cache.clear()

        all_docs = store.list_all()
        assert len(all_docs) == 2

    def test_json_serialization_format(self, temp_dir, sample_document):
        """Test documents are stored as valid JSON."""
        from app.storage.filesystem import FileSystemDocumentStore

        storage_path = temp_dir / "documents"
        store = FileSystemDocumentStore(base_path=storage_path)

        store.save(sample_document)

        doc_file = storage_path / f"{sample_document.id}.json"
        content = json.loads(doc_file.read_text())

        assert "id" in content
        assert "pages" in content
        assert content["id"] == sample_document.id


class TestStorageIntegration:
    """Integration tests for storage layer."""

    def test_document_roundtrip(self, temp_dir):
        """Test complete save-load-modify-save cycle."""
        from app.storage.filesystem import FileSystemDocumentStore
        from app.models import Document, Page, Block, BoundingBox

        storage_path = temp_dir / "documents"
        store = FileSystemDocumentStore(base_path=storage_path)

        # Create document with content
        block = Block(
            id="block-1",
            type="text",
            text="Original text",
            bbox=BoundingBox(x=10, y=20, width=100, height=50)
        )
        page = Page(number=1, width=612, height=792, blocks=[block])
        doc = Document(id="roundtrip-doc", pages=[page], metadata={})

        # Save
        store.save(doc)

        # Load
        loaded = store.get(doc.id)
        assert loaded.pages[0].blocks[0].text == "Original text"

        # Modify
        loaded.pages[0].blocks[0].text = "Modified text"
        store.save(loaded)

        # Reload
        reloaded = store.get(doc.id)
        assert reloaded.pages[0].blocks[0].text == "Modified text"

    def test_concurrent_access_safety(self, temp_dir, sample_document):
        """Test store handles concurrent-like access."""
        from app.storage.filesystem import FileSystemDocumentStore

        storage_path = temp_dir / "documents"

        # Simulate two store instances
        store1 = FileSystemDocumentStore(base_path=storage_path)
        store2 = FileSystemDocumentStore(base_path=storage_path)

        # Save from store1
        store1.save(sample_document)

        # Read from store2 (different cache)
        loaded = store2.get(sample_document.id)

        assert loaded is not None
        assert loaded.id == sample_document.id
