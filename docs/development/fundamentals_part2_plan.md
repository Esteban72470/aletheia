# Aletheia Fundamentals Part 2 - Implementation Plan

## Overview

Part 2 completes the foundational infrastructure by wiring up the pipeline components, adding persistence, completing API endpoints, and establishing proper test coverage.

**Status:** ✅ Complete
**Date:** January 28, 2026
**Prerequisite:** Fundamentals Part 1 Complete ✅

---

## Goals

1. **Wire Pipeline Components** - Connect orchestrator with loaders and OCR
2. **Add File Persistence** - Store documents to disk with cache
3. **Complete API Integration** - Query endpoint with document store
4. **Establish Test Suite** - pytest-based unit and integration tests
5. **Sample Documents** - Working minimal demo with sample files

---

## Task Breakdown

### Task 2.1: Pipeline Orchestrator Integration ⏳

**Goal:** Connect `PipelineOrchestrator` with actual loaders and OCR backends.

**Files to modify:**
- `sidecar/app/pipeline/orchestrator.py` - Full implementation
- `sidecar/app/pipeline/ingest/__init__.py` - Export loaders
- `sidecar/app/pipeline/ocr/__init__.py` - Export OCR backends

**Implementation:**
```python
# orchestrator.py enhancements
1. Import PDFLoader, ImageLoader from ingest/
2. Import TesseractBackend from ocr/
3. Implement full process() method:
   - Stage 1: File type detection and loading
   - Stage 2: Image preprocessing (if needed)
   - Stage 3: Layout detection (basic)
   - Stage 4: OCR for image-based pages
   - Stage 5: Block extraction and structuring
   - Stage 6: Return structured Document
```

**Acceptance Criteria:**
- [ ] PDF files parse with text extraction
- [ ] Image files process through OCR
- [ ] Blocks have accurate bounding boxes
- [ ] Multi-page documents supported

---

### Task 2.2: File-Based Document Persistence ⏳

**Goal:** Implement disk-based storage alongside in-memory cache.

**Files to create/modify:**
- `sidecar/app/storage/filesystem.py` - File storage implementation
- `sidecar/app/storage/cache.py` - Caching layer
- `sidecar/app/storage/__init__.py` - Export storage classes

**Implementation:**
```python
# filesystem.py
class FileSystemStore:
    def __init__(self, base_path: Path):
        self.base_path = base_path

    def save(self, document: Document) -> str:
        # Save as JSON to {base_path}/{doc_id}.json

    def get(self, document_id: str) -> Optional[Document]:
        # Load from JSON file

    def delete(self, document_id: str) -> bool:
        # Remove file

    def list(self) -> List[str]:
        # List all document IDs
```

**Cache Structure:**
```
~/.cache/aletheia/
├── documents/
│   ├── {doc_id}.json
│   └── ...
├── images/
│   ├── {doc_id}/
│   │   ├── page_1.png
│   │   └── page_2.png
│   └── ...
└── metadata.json
```

**Acceptance Criteria:**
- [ ] Documents persist across restarts
- [ ] Cache respects configurable size limits
- [ ] LRU eviction when cache full
- [ ] Atomic writes (no corruption)

---

### Task 2.3: Complete Query Endpoint ⏳

**Goal:** Wire query endpoint to document store and implement basic query logic.

**Files to modify:**
- `sidecar/app/api/query.py` - Full implementation
- `sidecar/app/main.py` - Inject document store

**Query Modes:**
1. **keyword** - Simple text search in blocks
2. **regex** - Pattern matching
3. **semantic** - (Placeholder for Phase 2)

**Implementation:**
```python
# query.py
@router.post("/query")
async def query_document(query: PerceptionQuery) -> QueryResponse:
    # 1. Get document from store
    doc = document_store.get(query.document_id)
    if not doc:
        raise HTTPException(404, "Document not found")

    # 2. Execute query based on mode
    results = []
    if query.mode == "keyword":
        results = keyword_search(doc, query.query)
    elif query.mode == "regex":
        results = regex_search(doc, query.query)

    # 3. Apply filters (page_range, block_types)
    results = apply_filters(results, query)

    # 4. Return response
    return QueryResponse(results=results[:query.max_results])
```

**Acceptance Criteria:**
- [ ] Keyword search returns matching blocks
- [ ] Results include block context
- [ ] Page range filtering works
- [ ] Block type filtering works

---

### Task 2.4: Unit Test Suite ⏳

**Goal:** Create comprehensive pytest test suite.

**Test Structure:**
```
tests/
├── sidecar/
│   ├── unit/
│   │   ├── test_models.py
│   │   ├── test_pipeline.py
│   │   ├── test_storage.py
│   │   └── test_api.py
│   └── integration/
│       ├── test_parse_flow.py
│       └── test_query_flow.py
├── cli/
│   ├── unit/
│   │   ├── test_commands.py
│   │   └── test_client.py
│   └── integration/
│       └── test_cli_flow.py
└── conftest.py
```

**Test Categories:**
1. **Models** - Pydantic validation, serialization
2. **Pipeline** - Loader functions, OCR calls
3. **Storage** - CRUD operations, persistence
4. **API** - Endpoint responses, error handling

**Acceptance Criteria:**
- [ ] 80%+ code coverage for sidecar
- [ ] All tests pass in CI
- [ ] Mocked external dependencies (tesseract, fitz)
- [ ] Fast test execution (<30s)

---

### Task 2.5: Sample Documents ⏳

**Goal:** Create working samples for minimal_demo.

**Files to create:**
- `examples/minimal_demo/sample.pdf` - Simple PDF with text
- `examples/minimal_demo/sample_image.png` - Image with text
- `examples/minimal_demo/expected_output.json` - Expected parse result

**Sample PDF Content:**
```
Page 1:
- Title: "Sample Document"
- Paragraph: "This is a test document for Aletheia."
- List: 3 items

Page 2:
- Table: 3x3 simple table
- Figure: placeholder
```

**Acceptance Criteria:**
- [ ] PDF parses without errors
- [ ] Image OCRs correctly
- [ ] Output matches expected schema
- [ ] Works offline

---

### Task 2.6: Fundamentals Part 2 Test Script ⏳

**Goal:** Create comprehensive test script like Part 1.

**File:** `tests/fundamentals/test_fundamentals_part2.py`

**Tests:**
1. Pipeline orchestrator integration
2. PDF loading and parsing
3. Image OCR processing
4. File storage persistence
5. Document retrieval
6. Query execution
7. Full parse-query flow

---

## Implementation Order

```
2.1 Pipeline Orchestrator ────┐
                              ├──► 2.4 Unit Tests
2.2 File Persistence ─────────┤
                              ├──► 2.6 Test Script
2.3 Query Endpoint ───────────┘
                              │
2.5 Sample Documents ─────────┘
```

---

## Definition of Done

### Part 2 Complete When:

- [ ] `aletheia parse sample.pdf` returns valid JSON
- [ ] `aletheia query {doc_id} "find text"` returns results
- [ ] Documents persist across sidecar restarts
- [ ] pytest suite passes with 80%+ coverage
- [ ] CI pipeline runs successfully
- [ ] No TODO placeholders in core code paths

---

## Files to Create/Modify

### New Files
| File                                            | Purpose                |
| ----------------------------------------------- | ---------------------- |
| `tests/sidecar/unit/test_models.py`             | Model unit tests       |
| `tests/sidecar/unit/test_pipeline.py`           | Pipeline unit tests    |
| `tests/sidecar/unit/test_storage.py`            | Storage unit tests     |
| `tests/sidecar/unit/test_api.py`                | API endpoint tests     |
| `tests/sidecar/integration/test_parse_flow.py`  | Parse integration test |
| `tests/sidecar/integration/test_query_flow.py`  | Query integration test |
| `tests/conftest.py`                             | pytest fixtures        |
| `tests/fundamentals/test_fundamentals_part2.py` | Part 2 verification    |
| `examples/minimal_demo/sample.pdf`              | Sample PDF             |
| `examples/minimal_demo/sample_image.png`        | Sample image           |

### Modified Files
| File                                      | Changes                   |
| ----------------------------------------- | ------------------------- |
| `sidecar/app/pipeline/orchestrator.py`    | Full implementation       |
| `sidecar/app/pipeline/ingest/__init__.py` | Export loaders            |
| `sidecar/app/pipeline/ocr/__init__.py`    | Export backends           |
| `sidecar/app/storage/filesystem.py`       | Implement FileSystemStore |
| `sidecar/app/storage/__init__.py`         | Export stores             |
| `sidecar/app/api/query.py`                | Full implementation       |
| `sidecar/app/main.py`                     | Inject dependencies       |

---

## Success Metrics

| Metric                      | Target |
| --------------------------- | ------ |
| Test Coverage               | ≥80%   |
| Parse Latency (1-page PDF)  | <500ms |
| Parse Latency (10-page PDF) | <3s    |
| Query Latency               | <100ms |
| Storage Write               | <50ms  |
| Storage Read                | <20ms  |

---

## Next: Fundamentals Part 3 (if needed)

- VS Code extension basic functionality
- CLI additional commands
- Docker compose setup
- CI/CD configuration

---

**Let's proceed with implementation! 🚀**
