"""Tesseract OCR backend."""

from typing import List

from PIL import Image

from app.pipeline.ocr.ocr_base import BaseOCR, OCRResult
from app.config import settings


class TesseractBackend(BaseOCR):
    """OCR using Tesseract."""

    def __init__(self, lang: str = None):
        """
        Initialize Tesseract backend.

        Args:
            lang: Language code (default from settings)
        """
        self.lang = lang or settings.tesseract_lang

    def recognize(self, image: Image.Image) -> OCRResult:
        """
        Perform OCR on an image using Tesseract.

        Args:
            image: Input image

        Returns:
            OCR result with text and confidence
        """
        import pytesseract

        # Get text with confidence data
        data = pytesseract.image_to_data(
            image,
            lang=self.lang,
            output_type=pytesseract.Output.DICT,
        )

        # Extract text
        text_parts = []
        confidences = []

        for i, word in enumerate(data["text"]):
            if word.strip():
                text_parts.append(word)
                conf = data["conf"][i]
                if conf != -1:
                    confidences.append(conf / 100.0)

        text = " ".join(text_parts)
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

        return OCRResult(
            text=text,
            confidence=avg_confidence,
        )

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
        # Crop the region
        x1, y1, x2, y2 = map(int, bbox)
        region = image.crop((x1, y1, x2, y2))

        return self.recognize(region)

    def get_word_boxes(self, image: Image.Image) -> List[dict]:
        """
        Get individual word bounding boxes.

        Args:
            image: Input image

        Returns:
            List of word boxes with text and coordinates
        """
        import pytesseract

        data = pytesseract.image_to_data(
            image,
            lang=self.lang,
            output_type=pytesseract.Output.DICT,
        )

        word_boxes = []
        for i, word in enumerate(data["text"]):
            if word.strip():
                word_boxes.append({
                    "text": word,
                    "bbox": [
                        data["left"][i],
                        data["top"][i],
                        data["left"][i] + data["width"][i],
                        data["top"][i] + data["height"][i],
                    ],
                    "confidence": data["conf"][i] / 100.0 if data["conf"][i] != -1 else 0.0,
                })

        return word_boxes
