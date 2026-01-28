"""Image loader for direct image files."""

from io import BytesIO
from typing import List, Optional

from PIL import Image

from app.pipeline.ingest.base import BaseLoader, LoadedPage


class ImageLoader(BaseLoader):
    """Load image files (PNG, JPEG, TIFF)."""

    SUPPORTED_TYPES = [
        "image/png",
        "image/jpeg",
        "image/tiff",
        "image/bmp",
        "image/webp",
    ]

    def can_handle(self, content_type: str) -> bool:
        """Check if this loader can handle the image type."""
        return content_type in self.SUPPORTED_TYPES

    def load(self, content: bytes, page_range: Optional[str] = None) -> List[LoadedPage]:
        """
        Load an image file.

        Args:
            content: Image file bytes
            page_range: Ignored for single images

        Returns:
            List with a single loaded page
        """
        image = Image.open(BytesIO(content))

        # Convert to RGB if necessary
        if image.mode not in ("RGB", "L"):
            image = image.convert("RGB")

        return [
            LoadedPage(
                page_number=1,
                image=image,
                width=image.width,
                height=image.height,
                text_layer=None,
            )
        ]
