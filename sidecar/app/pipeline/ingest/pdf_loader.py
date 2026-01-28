"""PDF document loader using PyMuPDF."""

from io import BytesIO
from typing import List, Optional

from PIL import Image

from app.pipeline.ingest.base import BaseLoader, LoadedPage
from app.config import settings


class PDFLoader(BaseLoader):
    """Load PDF documents using PyMuPDF (fitz)."""

    def can_handle(self, content_type: str) -> bool:
        """Check if this loader can handle PDFs."""
        return content_type == "application/pdf"

    def load(self, content: bytes, page_range: Optional[str] = None) -> List[LoadedPage]:
        """
        Load a PDF and convert pages to images.

        Args:
            content: PDF file bytes
            page_range: Optional page range

        Returns:
            List of loaded pages with images
        """
        # Import here to avoid startup cost if not needed
        import fitz  # PyMuPDF

        doc = fitz.open(stream=content, filetype="pdf")
        total_pages = len(doc)
        pages_to_load = self.parse_page_range(page_range, total_pages)

        loaded_pages = []

        for page_num in pages_to_load:
            if page_num > total_pages:
                continue

            page = doc[page_num - 1]

            # Render page to image at specified DPI
            mat = fitz.Matrix(settings.default_dpi / 72, settings.default_dpi / 72)
            pix = page.get_pixmap(matrix=mat)

            # Convert to PIL Image
            img_data = pix.tobytes("png")
            image = Image.open(BytesIO(img_data))

            # Extract text layer if available
            text_layer = page.get_text()

            loaded_pages.append(
                LoadedPage(
                    page_number=page_num,
                    image=image,
                    width=page.rect.width,
                    height=page.rect.height,
                    text_layer=text_layer if text_layer.strip() else None,
                )
            )

        doc.close()
        return loaded_pages
