"""Base OCR interface."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional

from PIL import Image


@dataclass
class OCRResult:
    """Result from OCR processing."""

    text: str
    confidence: float
    bbox: Optional[List[float]] = None  # [x1, y1, x2, y2]
    word_boxes: Optional[List[dict]] = None  # Individual word bounding boxes


class BaseOCR(ABC):
    """Abstract base class for OCR engines."""

    @abstractmethod
    def recognize(self, image: Image.Image) -> OCRResult:
        """
        Perform OCR on an image.

        Args:
            image: Input image

        Returns:
            OCR result with text and confidence
        """
        pass

    @abstractmethod
    def recognize_region(
        self, image: Image.Image, bbox: List[float]
    ) -> OCRResult:
        """
        Perform OCR on a specific region.

        Args:
            image: Full page image
            bbox: Region bounding box [x1, y1, x2, y2]

        Returns:
            OCR result for the region
        """
        pass

    def get_word_boxes(self, image: Image.Image) -> List[dict]:
        """
        Get individual word bounding boxes.

        Args:
            image: Input image

        Returns:
            List of word boxes with text and coordinates
        """
        return []
