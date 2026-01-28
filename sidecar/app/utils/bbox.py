"""Bounding box utilities."""

from typing import List, Tuple, Optional


class BBoxUtils:
    """Utilities for bounding box operations."""

    @staticmethod
    def normalize(
        bbox: List[float],
        width: float,
        height: float,
    ) -> List[float]:
        """
        Normalize bounding box to 0-1 range.

        Args:
            bbox: [x1, y1, x2, y2] in pixels
            width: Image width
            height: Image height

        Returns:
            Normalized bbox [x1, y1, x2, y2]
        """
        x1, y1, x2, y2 = bbox
        return [x1 / width, y1 / height, x2 / width, y2 / height]

    @staticmethod
    def denormalize(
        bbox: List[float],
        width: float,
        height: float,
    ) -> List[float]:
        """
        Denormalize bounding box from 0-1 range.

        Args:
            bbox: Normalized [x1, y1, x2, y2]
            width: Target width
            height: Target height

        Returns:
            Pixel bbox [x1, y1, x2, y2]
        """
        x1, y1, x2, y2 = bbox
        return [x1 * width, y1 * height, x2 * width, y2 * height]

    @staticmethod
    def iou(bbox1: List[float], bbox2: List[float]) -> float:
        """
        Calculate Intersection over Union (IoU).

        Args:
            bbox1: First bbox [x1, y1, x2, y2]
            bbox2: Second bbox [x1, y1, x2, y2]

        Returns:
            IoU value (0-1)
        """
        x1 = max(bbox1[0], bbox2[0])
        y1 = max(bbox1[1], bbox2[1])
        x2 = min(bbox1[2], bbox2[2])
        y2 = min(bbox1[3], bbox2[3])

        intersection = max(0, x2 - x1) * max(0, y2 - y1)

        area1 = (bbox1[2] - bbox1[0]) * (bbox1[3] - bbox1[1])
        area2 = (bbox2[2] - bbox2[0]) * (bbox2[3] - bbox2[1])

        union = area1 + area2 - intersection

        return intersection / union if union > 0 else 0.0

    @staticmethod
    def contains(outer: List[float], inner: List[float]) -> bool:
        """
        Check if outer bbox contains inner bbox.

        Args:
            outer: Outer bbox
            inner: Inner bbox

        Returns:
            True if outer contains inner
        """
        return (
            outer[0] <= inner[0]
            and outer[1] <= inner[1]
            and outer[2] >= inner[2]
            and outer[3] >= inner[3]
        )

    @staticmethod
    def merge(bboxes: List[List[float]]) -> Optional[List[float]]:
        """
        Merge multiple bboxes into one enclosing bbox.

        Args:
            bboxes: List of bboxes

        Returns:
            Merged bbox or None if empty
        """
        if not bboxes:
            return None

        x1 = min(b[0] for b in bboxes)
        y1 = min(b[1] for b in bboxes)
        x2 = max(b[2] for b in bboxes)
        y2 = max(b[3] for b in bboxes)

        return [x1, y1, x2, y2]

    @staticmethod
    def area(bbox: List[float]) -> float:
        """
        Calculate bbox area.

        Args:
            bbox: Bounding box

        Returns:
            Area in square units
        """
        return (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
