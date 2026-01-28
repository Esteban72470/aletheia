# Aletheia Phase 1 Part 1 - Layout Analysis

## Overview

Phase 1 Part 1 focuses on implementing enhanced layout analysis capabilities using LayoutParser and improving block segmentation.

**Status:** 🚧 In Progress
**Date:** January 28, 2026
**Prerequisite:** Fundamentals Complete ✅

---

## Goals

1. **LayoutParser Integration** - Implement document layout detection
2. **Block Segmentation** - Better identification of document regions
3. **Reading Order** - Accurate text flow detection
4. **Block Classification** - Semantic labeling of regions

---

## Task Breakdown

### Task 1.1: LayoutParser Backend Implementation

**Goal:** Complete the LayoutParser backend for document layout detection.

**Files to modify:**
- `sidecar/app/pipeline/layout/layoutparser_backend.py` - Full implementation
- `sidecar/app/pipeline/layout/layout_base.py` - Base classes (if needed)
- `sidecar/app/pipeline/layout/__init__.py` - Exports

**Implementation:**
```python
# LayoutParser backend features:
1. Model loading with fallback (Detectron2 or lightweight)
2. Layout detection on page images
3. Block type classification (Text, Title, List, Table, Figure)
4. Confidence scores for each detection
5. Reading order calculation
```

**Acceptance Criteria:**
- [ ] Model loads successfully (or graceful fallback)
- [ ] Detects blocks on sample documents
- [ ] Returns proper LayoutBlock objects
- [ ] Handles various document types

---

### Task 1.2: Orchestrator Layout Integration

**Goal:** Wire layout detection into the main pipeline.

**Files to modify:**
- `sidecar/app/pipeline/orchestrator.py` - Add layout stage
- `sidecar/app/api/models.py` - Add layout-related response fields

**Pipeline Enhancement:**
```
Current:  Ingest → OCR → PostProcess
Enhanced: Ingest → PreProcess → Layout → OCR → PostProcess
                              ↑
                       (New Stage)
```

**Acceptance Criteria:**
- [ ] Layout detection runs before OCR
- [ ] Block regions guide OCR processing
- [ ] Parse response includes layout info
- [ ] Configurable via parse options

---

### Task 1.3: Alternative Layout Detection

**Goal:** Provide fallback when LayoutParser not available.

**Files to create:**
- `sidecar/app/pipeline/layout/heuristic_backend.py` - Rule-based detection

**Features:**
- Whitespace-based block detection
- Line grouping into paragraphs
- Header detection by font size
- List detection by indentation

---

### Task 1.4: Unit Tests for Layout

**Files to create:**
- `tests/sidecar/unit/test_layout.py` - Layout component tests

**Test Coverage:**
- Backend initialization
- Block detection
- Reading order
- Block type classification
- Fallback behavior

---

## Implementation Order

```
1.1 LayoutParser Backend ─────┐
                              ├──► 1.4 Unit Tests
1.3 Heuristic Fallback ───────┤
                              │
1.2 Orchestrator Integration ─┘
```

---

## Success Criteria

| Metric                   | Target                  |
| ------------------------ | ----------------------- |
| Block Detection Accuracy | ≥ 85%                   |
| Layout Detection Latency | < 500ms per page        |
| Fallback Coverage        | 100% documents work     |
| Test Coverage            | ≥ 80% for layout module |

---

## Technical Notes

### LayoutParser Models

Available pretrained models:
- `lp://PubLayNet/faster_rcnn/R_50_FPN_3x` - Academic papers
- `lp://PrimaLayout/mask_rcnn_R_50_FPN_3x` - Magazines
- `lp://TableBank/faster_rcnn_R_101_FPN_3x` - Tables only

### Block Types

Standard block types for classification:
- `heading` - Section titles
- `paragraph` - Body text
- `list` - Bulleted/numbered lists
- `table` - Tabular data
- `figure` - Images/diagrams
- `caption` - Figure/table captions
- `header` - Page headers
- `footer` - Page footers
- `other` - Unclassified

---

## Files to Create/Modify

### New Files
| File                                               | Purpose                     |
| -------------------------------------------------- | --------------------------- |
| `sidecar/app/pipeline/layout/heuristic_backend.py` | Fallback detection          |
| `tests/sidecar/unit/test_layout.py`                | Layout unit tests           |
| `tests/phase1/test_phase1_part1.py`                | Phase 1 Part 1 verification |

### Modified Files
| File                                                  | Changes                  |
| ----------------------------------------------------- | ------------------------ |
| `sidecar/app/pipeline/layout/layoutparser_backend.py` | Full implementation      |
| `sidecar/app/pipeline/orchestrator.py`                | Layout stage integration |
| `sidecar/app/api/models.py`                           | Layout response fields   |

---

**Let's begin implementation! 🚀**
