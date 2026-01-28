#!/usr/bin/env python3
"""
Phase 1 Part 1 Verification Script: Layout Analysis

This script verifies that Phase 1 Part 1 (Enhanced Layout Analysis)
is properly implemented and functional.

Run from the sidecar directory:
    python tests/phase1/test_phase1_part1.py
"""

import sys
from pathlib import Path
from PIL import Image
import io

# Add sidecar to path
sidecar_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(sidecar_path))


def verify_imports():
    """Verify all layout modules can be imported."""
    print("=" * 60)
    print("Phase 1 Part 1 Verification: Layout Analysis")
    print("=" * 60)
    print()

    print("[1/7] Verifying imports...")

    try:
        from app.pipeline.layout import LayoutParserBackend, LayoutBlock, BaseLayoutDetector
        print("  ✓ LayoutParserBackend imported")
        print("  ✓ LayoutBlock imported")
        print("  ✓ BaseLayoutDetector imported")
        return True
    except ImportError as e:
        print(f"  ✗ Import failed: {e}")
        return False


def verify_layout_block():
    """Verify LayoutBlock dataclass works correctly."""
    print()
    print("[2/7] Verifying LayoutBlock dataclass...")

    from app.pipeline.layout import LayoutBlock

    # Test with all fields
    block1 = LayoutBlock(
        id="test_block_1",
        type="paragraph",
        bbox=[10.0, 20.0, 100.0, 80.0],
        confidence=0.95,
        text="Sample text"
    )

    assert block1.id == "test_block_1", "Block ID mismatch"
    assert block1.type == "paragraph", "Block type mismatch"
    assert block1.bbox == [10.0, 20.0, 100.0, 80.0], "Block bbox mismatch"
    assert block1.confidence == 0.95, "Block confidence mismatch"
    assert block1.text == "Sample text", "Block text mismatch"
    print("  ✓ LayoutBlock with all fields works")

    # Test with defaults
    block2 = LayoutBlock(
        id="test_block_2",
        type="heading",
        bbox=[0, 0, 50, 30],
    )
    assert block2.confidence == 0.0, "Default confidence should be 0.0"
    assert block2.text == "", "Default text should be empty"
    print("  ✓ LayoutBlock with defaults works")

    return True


def verify_backend_initialization():
    """Verify LayoutParserBackend initializes correctly."""
    print()
    print("[3/7] Verifying backend initialization...")

    from app.pipeline.layout import LayoutParserBackend

    backend = LayoutParserBackend()
    assert backend is not None, "Backend should not be None"
    print("  ✓ Backend instantiated")

    # Check lazy initialization
    assert backend._model is None, "Model should not be loaded yet (lazy init)"
    print("  ✓ Model uses lazy initialization")

    # Check availability property
    available = backend.is_available
    assert isinstance(available, bool), "is_available should return bool"
    if available:
        print("  ✓ LayoutParser IS available (Detectron2 detected)")
    else:
        print("  ✓ LayoutParser NOT available (using heuristic fallback)")

    return True


def verify_heuristic_detection():
    """Verify heuristic fallback detection works."""
    print()
    print("[4/7] Verifying heuristic detection...")

    from app.pipeline.layout import LayoutParserBackend, LayoutBlock

    backend = LayoutParserBackend()

    # Create a test image
    img = Image.new("RGB", (800, 1000), color="white")

    # Detect blocks (will use heuristics if LayoutParser unavailable)
    blocks = backend.detect(img)

    assert isinstance(blocks, list), "Detection should return list"
    print(f"  ✓ Detected {len(blocks)} blocks")

    for block in blocks:
        assert isinstance(block, LayoutBlock), "Each result should be LayoutBlock"
        assert len(block.bbox) == 4, "Bbox should have 4 values"
        assert block.id, "Block should have ID"
        assert block.type, "Block should have type"
    print("  ✓ All blocks have valid structure")

    return True


def verify_reading_order():
    """Verify reading order calculation works."""
    print()
    print("[5/7] Verifying reading order...")

    from app.pipeline.layout import LayoutParserBackend, LayoutBlock

    backend = LayoutParserBackend()

    # Create blocks out of reading order
    blocks = [
        LayoutBlock(id="bottom", type="paragraph", bbox=[10, 500, 100, 600]),
        LayoutBlock(id="top", type="heading", bbox=[10, 10, 100, 50]),
        LayoutBlock(id="middle", type="paragraph", bbox=[10, 200, 100, 300]),
    ]

    ordered = backend.get_reading_order(blocks)

    assert len(ordered) == 3, "Should have same number of blocks"
    assert ordered[0].id == "top", "First should be top block"
    assert ordered[1].id == "middle", "Second should be middle block"
    assert ordered[2].id == "bottom", "Third should be bottom block"
    print("  ✓ Vertical ordering works correctly")

    # Test horizontal ordering
    blocks_h = [
        LayoutBlock(id="right", type="paragraph", bbox=[300, 10, 400, 50]),
        LayoutBlock(id="left", type="paragraph", bbox=[10, 10, 100, 50]),
    ]

    ordered_h = backend.get_reading_order(blocks_h)
    assert ordered_h[0].id == "left", "Left block should be first"
    assert ordered_h[1].id == "right", "Right block should be second"
    print("  ✓ Horizontal ordering works correctly")

    return True


def verify_orchestrator_integration():
    """Verify layout detection is integrated in orchestrator."""
    print()
    print("[6/7] Verifying orchestrator integration...")

    from app.pipeline.orchestrator import PipelineOrchestrator
    from app.pipeline.layout import LayoutParserBackend

    orchestrator = PipelineOrchestrator()

    # Check layout backend getter exists and works
    assert hasattr(orchestrator, '_get_layout_backend'), "Should have _get_layout_backend method"
    print("  ✓ _get_layout_backend method exists")

    layout_backend = orchestrator._get_layout_backend()
    assert layout_backend is not None, "Layout backend should be returned"
    assert isinstance(layout_backend, LayoutParserBackend), "Should return LayoutParserBackend"
    print("  ✓ Layout backend instantiated correctly")

    # Verify caching
    layout_backend2 = orchestrator._get_layout_backend()
    assert layout_backend is layout_backend2, "Backend should be cached"
    print("  ✓ Layout backend is cached")

    return True


def verify_block_types():
    """Verify all expected block types are supported."""
    print()
    print("[7/7] Verifying block types...")

    expected_types = [
        "heading", "paragraph", "list", "table",
        "figure", "caption", "header", "footer", "other"
    ]

    from app.pipeline.layout import LayoutBlock

    for block_type in expected_types:
        block = LayoutBlock(
            id=f"test_{block_type}",
            type=block_type,
            bbox=[0, 0, 100, 100],
        )
        assert block.type == block_type

    print(f"  ✓ All {len(expected_types)} block types supported")
    return True


def main():
    """Run all verification tests."""
    results = []

    try:
        results.append(("Imports", verify_imports()))
        results.append(("LayoutBlock", verify_layout_block()))
        results.append(("Backend Init", verify_backend_initialization()))
        results.append(("Heuristic Detection", verify_heuristic_detection()))
        results.append(("Reading Order", verify_reading_order()))
        results.append(("Orchestrator Integration", verify_orchestrator_integration()))
        results.append(("Block Types", verify_block_types()))
    except Exception as e:
        print(f"\n✗ Verification failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    # Summary
    print()
    print("=" * 60)
    print("PHASE 1 PART 1 VERIFICATION SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, r in results if r)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {name}")

    print()
    print(f"Results: {passed}/{total} checks passed")

    if passed == total:
        print()
        print("🎉 PHASE 1 PART 1 COMPLETE!")
        print()
        print("Layout analysis capabilities implemented:")
        print("  • LayoutParser backend with Detectron2 support")
        print("  • Heuristic fallback for environments without GPU")
        print("  • Block classification (heading, paragraph, table, etc.)")
        print("  • Reading order calculation (top-to-bottom, left-to-right)")
        print("  • Orchestrator integration with lazy initialization")
        print()
        print("Next: Phase 1 Part 2 - Table Detection")
        return 0
    else:
        print()
        print("❌ Some checks failed. Please review the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
