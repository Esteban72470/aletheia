"""Base layout detector interface."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List

from PIL import Image


@dataclass
class LayoutBlock:
    """A detected layout block."""

    id: str
    type: str  # paragraph, heading, table, figure, list, etc.
    bbox: List[float]  # [x1, y1, x2, y2]
    confidence: float = 0.0
    text: str = ""


class BaseLayoutDetector(ABC):
    """Abstract base class for layout detection."""

    @abstractmethod
    def detect(self, image: Image.Image) -> List[LayoutBlock]:
        """
        Detect layout blocks in an image.

        Args:
            image: Page image

        Returns:
            List of detected layout blocks
        """
        pass

    @abstractmethod
    def get_reading_order(self, blocks: List[LayoutBlock]) -> List[LayoutBlock]:
        """
        Sort blocks in reading order.

        Args:
            blocks: Detected blocks

        Returns:
            Blocks sorted in reading order
        """
        pass
