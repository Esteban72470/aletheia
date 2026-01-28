"""Unit tests for layout detection module."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from PIL import Image
import numpy as np

from app.pipeline.layout import LayoutParserBackend, LayoutBlock


class TestLayoutBlock:
    """Tests for LayoutBlock dataclass."""

    def test_layout_block_creation(self):
        """Test creating a layout block with all fields."""
        block = LayoutBlock(
            id="block_1",
            type="paragraph",
            bbox=[10.0, 20.0, 100.0, 80.0],
            confidence=0.95,
        )

        assert block.id == "block_1"
        assert block.type == "paragraph"
        assert block.bbox == [10.0, 20.0, 100.0, 80.0]
        assert block.confidence == 0.95

    def test_layout_block_default_values(self):
        """Test layout block with minimal required fields."""
        block = LayoutBlock(
            id="block_2",
            type="heading",
            bbox=[0, 0, 50, 30],
        )

        assert block.id == "block_2"
        assert block.type == "heading"
        assert block.bbox == [0, 0, 50, 30]
        assert block.confidence == 0.0  # Default value

    def test_layout_block_types(self):
        """Test various valid block types."""
        valid_types = [
            "heading", "paragraph", "list", "table",
            "figure", "caption", "header", "footer", "other"
        ]

        for block_type in valid_types:
            block = LayoutBlock(
                id=f"block_{block_type}",
                type=block_type,
                bbox=[0, 0, 100, 100],
            )
            assert block.type == block_type


class TestLayoutParserBackend:
    """Tests for LayoutParserBackend."""

    @pytest.fixture
    def backend(self):
        """Create a layout parser backend instance."""
        return LayoutParserBackend()

    @pytest.fixture
    def sample_image(self):
        """Create a sample test image."""
        # Create a simple test image with some content
        img = Image.new("RGB", (800, 1000), color="white")
        return img

    @pytest.fixture
    def sample_image_with_regions(self):
        """Create a test image with visible regions for heuristic detection."""
        # Create an image with dark regions (simulating text)
        img = Image.new("RGB", (800, 1000), color="white")
        from PIL import ImageDraw
        draw = ImageDraw.Draw(img)

        # Draw a "heading" region at top
        draw.rectangle([100, 50, 700, 100], fill=(50, 50, 50))

        # Draw "paragraph" lines below
        for y in range(150, 400, 30):
            draw.rectangle([50, y, 750, y + 20], fill=(80, 80, 80))

        return img

    def test_backend_initialization(self, backend):
        """Test backend initializes correctly."""
        assert backend is not None
        # Backend should start without model loaded (lazy init)
        assert backend._model is None

    def test_is_available_property(self, backend):
        """Test is_available property reflects layoutparser availability."""
        # Should return True if layoutparser is available, False otherwise
        available = backend.is_available
        assert isinstance(available, bool)

    def test_detect_returns_list(self, backend, sample_image):
        """Test detect always returns a list."""
        result = backend.detect(sample_image)
        assert isinstance(result, list)

    def test_detect_returns_layout_blocks(self, backend, sample_image):
        """Test detect returns LayoutBlock instances."""
        result = backend.detect(sample_image)
        for block in result:
            assert isinstance(block, LayoutBlock)

    def test_detect_blocks_have_valid_bboxes(self, backend, sample_image):
        """Test detected blocks have valid bounding boxes."""
        result = backend.detect(sample_image)

        img_width, img_height = sample_image.size
        for block in result:
            assert len(block.bbox) == 4
            x1, y1, x2, y2 = block.bbox
            assert x1 >= 0
            assert y1 >= 0
            assert x2 <= img_width
            assert y2 <= img_height
            assert x1 < x2  # Valid width
            assert y1 < y2  # Valid height

    def test_detect_with_regions(self, backend, sample_image_with_regions):
        """Test detection on image with visible regions."""
        result = backend.detect(sample_image_with_regions)

        # Should detect at least one block
        assert len(result) >= 1

        # All blocks should be valid
        for block in result:
            assert block.id
            assert block.type
            assert len(block.bbox) == 4

    def test_detect_empty_image(self, backend):
        """Test detection on empty/blank image."""
        blank_img = Image.new("RGB", (400, 600), color="white")
        result = backend.detect(blank_img)

        # Should return at least one block (full-page fallback)
        assert len(result) >= 1

    def test_get_reading_order_empty_list(self, backend):
        """Test reading order on empty list."""
        result = backend.get_reading_order([])
        assert result == []

    def test_get_reading_order_single_block(self, backend):
        """Test reading order with single block."""
        blocks = [LayoutBlock(id="b1", type="paragraph", bbox=[10, 10, 100, 100])]
        result = backend.get_reading_order(blocks)

        assert len(result) == 1
        assert result[0].id == "b1"

    def test_get_reading_order_vertical(self, backend):
        """Test reading order sorts vertically."""
        blocks = [
            LayoutBlock(id="bottom", type="paragraph", bbox=[10, 200, 100, 300]),
            LayoutBlock(id="top", type="heading", bbox=[10, 10, 100, 50]),
            LayoutBlock(id="middle", type="paragraph", bbox=[10, 100, 100, 150]),
        ]

        result = backend.get_reading_order(blocks)

        # Should be ordered top to bottom
        assert result[0].id == "top"
        assert result[1].id == "middle"
        assert result[2].id == "bottom"

    def test_get_reading_order_horizontal_same_row(self, backend):
        """Test reading order sorts horizontally within same row."""
        blocks = [
            LayoutBlock(id="right", type="paragraph", bbox=[300, 10, 400, 50]),
            LayoutBlock(id="left", type="paragraph", bbox=[10, 10, 100, 50]),
            LayoutBlock(id="center", type="paragraph", bbox=[150, 10, 250, 50]),
        ]

        result = backend.get_reading_order(blocks)

        # Should be ordered left to right
        assert result[0].id == "left"
        assert result[1].id == "center"
        assert result[2].id == "right"

    def test_get_reading_order_two_columns(self, backend):
        """Test reading order with two-column layout."""
        blocks = [
            # Left column
            LayoutBlock(id="left_1", type="paragraph", bbox=[10, 10, 200, 100]),
            LayoutBlock(id="left_2", type="paragraph", bbox=[10, 120, 200, 200]),
            # Right column
            LayoutBlock(id="right_1", type="paragraph", bbox=[250, 10, 400, 100]),
            LayoutBlock(id="right_2", type="paragraph", bbox=[250, 120, 400, 200]),
        ]

        result = backend.get_reading_order(blocks)

        # Should handle columns - reading left column first, then right
        # With the row-based algorithm, items in same row go left-to-right
        ids = [b.id for b in result]

        # First row: left_1 before right_1
        assert ids.index("left_1") < ids.index("right_1")
        # Second row: left_2 before right_2
        assert ids.index("left_2") < ids.index("right_2")

    def test_detect_with_none_image(self, backend):
        """Test detect handles None gracefully."""
        # Should raise or return empty depending on implementation
        try:
            result = backend.detect(None)
            assert result == [] or isinstance(result, list)
        except (TypeError, ValueError):
            pass  # Expected if implementation validates input


class TestLayoutParserBackendHeuristics:
    """Tests specifically for heuristic fallback detection."""

    @pytest.fixture
    def backend(self):
        """Create backend that uses heuristics."""
        return LayoutParserBackend()

    def test_heuristic_classification_heading(self, backend):
        """Test heading classification heuristics."""
        # Wide, short region at top of page should be heading
        region = {"x": 100, "y": 10, "width": 600, "height": 40}
        page_height = 1000

        block_type = backend._classify_region_type(region, page_height)

        # At top and wide - likely heading
        assert block_type in ("heading", "header", "paragraph")

    def test_heuristic_classification_footer(self, backend):
        """Test footer classification heuristics."""
        # Region at very bottom of page
        region = {"x": 100, "y": 950, "width": 200, "height": 30}
        page_height = 1000

        block_type = backend._classify_region_type(region, page_height)

        assert block_type == "footer"

    def test_heuristic_classification_paragraph(self, backend):
        """Test paragraph classification heuristics."""
        # Large region in middle of page
        region = {"x": 50, "y": 200, "width": 700, "height": 300}
        page_height = 1000

        block_type = backend._classify_region_type(region, page_height)

        assert block_type == "paragraph"


class TestLayoutIntegration:
    """Integration tests for layout detection."""

    @pytest.fixture
    def backend(self):
        """Create a layout parser backend."""
        return LayoutParserBackend()

    def test_full_detection_pipeline(self, backend):
        """Test complete detection and ordering pipeline."""
        # Create test image
        img = Image.new("RGB", (800, 1000), color="white")

        # Detect blocks
        blocks = backend.detect(img)

        # Order blocks
        ordered = backend.get_reading_order(blocks)

        # Verify pipeline produces valid output
        assert isinstance(ordered, list)
        for block in ordered:
            assert isinstance(block, LayoutBlock)
            assert block.id
            assert block.type
            assert len(block.bbox) == 4

    def test_detection_reproducibility(self, backend):
        """Test that same image produces consistent results."""
        img = Image.new("RGB", (400, 600), color="white")

        result1 = backend.detect(img)
        result2 = backend.detect(img)

        # Results should be consistent
        assert len(result1) == len(result2)

        for b1, b2 in zip(result1, result2):
            assert b1.type == b2.type
            assert b1.bbox == b2.bbox


# Mocking tests for when LayoutParser IS available
class TestLayoutParserWithModel:
    """Tests that mock LayoutParser availability."""

    @patch('app.pipeline.layout.layoutparser_backend._LAYOUTPARSER_AVAILABLE', True)
    def test_model_detection_mocked(self):
        """Test detection with mocked layoutparser model."""
        with patch.object(LayoutParserBackend, '_load_model') as mock_load:
            # Mock the model return
            mock_model = MagicMock()
            mock_load.return_value = mock_model

            # Mock detection result
            mock_layout = MagicMock()
            mock_layout.__iter__ = Mock(return_value=iter([]))
            mock_model.detect.return_value = mock_layout

            backend = LayoutParserBackend()
            backend._model = mock_model

            img = Image.new("RGB", (100, 100), "white")

            # Detection should use model when available
            # (actual behavior depends on implementation)
            result = backend.detect(img)
            assert isinstance(result, list)
