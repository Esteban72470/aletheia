"""LayoutParser backend for layout detection."""

import logging
from typing import List, Optional
from uuid import uuid4

from PIL import Image
import numpy as np

from app.pipeline.layout.layout_base import BaseLayoutDetector, LayoutBlock

logger = logging.getLogger(__name__)

# Try to import layoutparser and detectron2
_LAYOUTPARSER_AVAILABLE = False
_lp = None

try:
    import layoutparser as lp
    _lp = lp
    _LAYOUTPARSER_AVAILABLE = True
    logger.info("LayoutParser is available")
except ImportError:
    logger.warning("LayoutParser not installed. Using fallback heuristic detection.")


class LayoutParserBackend(BaseLayoutDetector):
    """Layout detection using LayoutParser library with fallback support."""

    # Available pretrained models
    MODELS = {
        "publaynet": "lp://PubLayNet/faster_rcnn/R_50_FPN_3x",
        "prima": "lp://PrimaLayout/mask_rcnn_R_50_FPN_3x",
        "tablebank": "lp://TableBank/faster_rcnn_R_101_FPN_3x",
    }

    # PubLayNet label mapping
    PUBLAYNET_LABELS = {
        0: "text",
        1: "title",
        2: "list",
        3: "table",
        4: "figure",
    }

    def __init__(
        self,
        model_name: str = "publaynet",
        confidence_threshold: float = 0.5,
        use_fallback: bool = True,
    ):
        """
        Initialize LayoutParser backend.

        Args:
            model_name: Model name or LayoutParser model identifier
            confidence_threshold: Minimum confidence for detections
            use_fallback: Whether to use heuristic fallback if model unavailable
        """
        self.model_identifier = self.MODELS.get(model_name, model_name)
        self.confidence_threshold = confidence_threshold
        self.use_fallback = use_fallback
        self._model = None
        self._initialized = False

    def _load_model(self) -> bool:
        """
        Lazy load the model.

        Returns:
            True if model loaded successfully, False otherwise
        """
        if self._initialized:
            return self._model is not None

        self._initialized = True

        if not _LAYOUTPARSER_AVAILABLE:
            logger.warning("LayoutParser not available, using fallback")
            return False

        try:
            self._model = _lp.Detectron2LayoutModel(
                self.model_identifier,
                extra_config=["MODEL.ROI_HEADS.SCORE_THRESH_TEST", self.confidence_threshold],
                label_map=self.PUBLAYNET_LABELS,
            )
            logger.info(f"Loaded LayoutParser model: {self.model_identifier}")
            return True
        except Exception as e:
            logger.error(f"Failed to load LayoutParser model: {e}")
            self._model = None
            return False

    def detect(self, image: Image.Image) -> List[LayoutBlock]:
        """
        Detect layout blocks using LayoutParser or fallback.

        Args:
            image: Page image

        Returns:
            List of detected layout blocks
        """
        model_loaded = self._load_model()

        if model_loaded and self._model is not None:
            return self._detect_with_model(image)
        elif self.use_fallback:
            return self._detect_with_heuristics(image)
        else:
            return []

    def _detect_with_model(self, image: Image.Image) -> List[LayoutBlock]:
        """Detect blocks using LayoutParser model."""
        try:
            # Convert PIL Image to numpy array for layoutparser
            img_array = np.array(image)

            # Run detection
            layout = self._model.detect(img_array)

            blocks = []
            for idx, block in enumerate(layout):
                layout_block = LayoutBlock(
                    id=f"block-{uuid4().hex[:8]}",
                    type=self._normalize_type(block.type),
                    bbox=[
                        float(block.block.x_1),
                        float(block.block.y_1),
                        float(block.block.x_2),
                        float(block.block.y_2),
                    ],
                    confidence=float(block.score) if hasattr(block, 'score') else 0.9,
                    text="",  # Text will be filled by OCR stage
                )
                blocks.append(layout_block)

            logger.debug(f"Detected {len(blocks)} blocks with LayoutParser")
            return blocks

        except Exception as e:
            logger.error(f"LayoutParser detection failed: {e}")
            if self.use_fallback:
                return self._detect_with_heuristics(image)
            return []

    def _detect_with_heuristics(self, image: Image.Image) -> List[LayoutBlock]:
        """
        Fallback heuristic-based block detection.

        Uses image analysis to detect text regions based on:
        - Connected component analysis
        - Whitespace detection
        - Region merging
        """
        try:
            # Convert to grayscale
            if image.mode != 'L':
                gray = image.convert('L')
            else:
                gray = image

            img_array = np.array(gray)
            width, height = image.size

            # Simple threshold to find text regions
            threshold = 200
            binary = img_array < threshold

            # Find horizontal projections to detect text lines
            h_proj = np.sum(binary, axis=1)

            # Find regions with content
            blocks = []
            in_region = False
            region_start = 0
            min_region_height = 10

            for y, val in enumerate(h_proj):
                if val > width * 0.01 and not in_region:
                    in_region = True
                    region_start = y
                elif val <= width * 0.01 and in_region:
                    in_region = False
                    if y - region_start > min_region_height:
                        # Find horizontal extent
                        region_slice = binary[region_start:y, :]
                        v_proj = np.sum(region_slice, axis=0)
                        x_start = np.argmax(v_proj > 0)
                        x_end = len(v_proj) - np.argmax(v_proj[::-1] > 0)

                        block = LayoutBlock(
                            id=f"block-{uuid4().hex[:8]}",
                            type=self._classify_region_type(
                                y - region_start,
                                x_end - x_start,
                                width,
                                height
                            ),
                            bbox=[float(x_start), float(region_start),
                                  float(x_end), float(y)],
                            confidence=0.7,  # Lower confidence for heuristic
                            text="",
                        )
                        blocks.append(block)

            # Handle case where document ends in a region
            if in_region and height - region_start > min_region_height:
                blocks.append(LayoutBlock(
                    id=f"block-{uuid4().hex[:8]}",
                    type="paragraph",
                    bbox=[0.0, float(region_start), float(width), float(height)],
                    confidence=0.6,
                    text="",
                ))

            logger.debug(f"Detected {len(blocks)} blocks with heuristics")
            return blocks if blocks else self._create_full_page_block(width, height)

        except Exception as e:
            logger.error(f"Heuristic detection failed: {e}")
            return self._create_full_page_block(image.size[0], image.size[1])

    def _create_full_page_block(self, width: int, height: int) -> List[LayoutBlock]:
        """Create a single block covering the full page as ultimate fallback."""
        return [LayoutBlock(
            id=f"block-{uuid4().hex[:8]}",
            type="paragraph",
            bbox=[0.0, 0.0, float(width), float(height)],
            confidence=0.5,
            text="",
        )]

    def _classify_region_type(
        self,
        region_height: int,
        region_width: int,
        page_width: int,
        page_height: int
    ) -> str:
        """
        Classify region type based on dimensions and position.

        Heuristics:
        - Short, wide regions near top = heading
        - Tall regions = paragraph
        - Very wide = full-width paragraph
        - Narrow, repeated = list
        """
        height_ratio = region_height / page_height
        width_ratio = region_width / page_width

        # Heading: short and at least half width
        if height_ratio < 0.05 and width_ratio > 0.4:
            return "heading"

        # Wide paragraph
        if width_ratio > 0.7:
            return "paragraph"

        # Narrower content might be list or column
        if width_ratio < 0.5:
            return "list"

        return "paragraph"

    def _normalize_type(self, block_type: str) -> str:
        """Normalize block type to standard names."""
        type_map = {
            "text": "paragraph",
            "title": "heading",
            "list": "list",
            "table": "table",
            "figure": "figure",
            "caption": "caption",
            "header": "header",
            "footer": "footer",
        }
        return type_map.get(str(block_type).lower(), "other")

    def get_reading_order(self, blocks: List[LayoutBlock]) -> List[LayoutBlock]:
        """
        Sort blocks in reading order (top-to-bottom, left-to-right).

        Uses a two-pass approach:
        1. Group blocks by approximate vertical position
        2. Sort within each group by horizontal position

        Args:
            blocks: Detected blocks

        Returns:
            Blocks sorted in reading order
        """
        if not blocks:
            return blocks

        # Calculate average line height for grouping
        heights = [b.bbox[3] - b.bbox[1] for b in blocks]
        avg_height = sum(heights) / len(heights) if heights else 50
        line_tolerance = avg_height * 0.5

        # Group blocks by vertical position
        lines: List[List[LayoutBlock]] = []
        sorted_by_y = sorted(blocks, key=lambda b: b.bbox[1])

        current_line: List[LayoutBlock] = []
        current_y = -1000

        for block in sorted_by_y:
            block_y = block.bbox[1]
            if abs(block_y - current_y) < line_tolerance:
                current_line.append(block)
            else:
                if current_line:
                    lines.append(current_line)
                current_line = [block]
                current_y = block_y

        if current_line:
            lines.append(current_line)

        # Sort each line left-to-right and flatten
        result = []
        for line in lines:
            line_sorted = sorted(line, key=lambda b: b.bbox[0])
            result.extend(line_sorted)

        return result

    @property
    def is_available(self) -> bool:
        """Check if LayoutParser model is available."""
        return _LAYOUTPARSER_AVAILABLE and self._load_model()
