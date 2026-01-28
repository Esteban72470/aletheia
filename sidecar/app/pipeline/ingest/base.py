"""Base loader interface."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional

from PIL import Image


@dataclass
class LoadedPage:
    """A loaded page ready for processing."""

    page_number: int
    image: Image.Image
    width: float
    height: float
    text_layer: Optional[str] = None  # For PDFs with embedded text


class BaseLoader(ABC):
    """Abstract base class for document loaders."""

    @abstractmethod
    def can_handle(self, content_type: str) -> bool:
        """Check if this loader can handle the given content type."""
        pass

    @abstractmethod
    def load(self, content: bytes, page_range: Optional[str] = None) -> List[LoadedPage]:
        """
        Load a document and return pages.

        Args:
            content: Raw file bytes
            page_range: Optional page range string (e.g., "1-5")

        Returns:
            List of loaded pages
        """
        pass

    def parse_page_range(self, page_range: Optional[str], total_pages: int) -> List[int]:
        """Parse a page range string into a list of page numbers."""
        if not page_range:
            return list(range(1, total_pages + 1))

        pages = []
        for part in page_range.split(","):
            if "-" in part:
                start, end = map(int, part.split("-"))
                pages.extend(range(start, min(end + 1, total_pages + 1)))
            else:
                page = int(part)
                if 1 <= page <= total_pages:
                    pages.append(page)

        return sorted(set(pages))
