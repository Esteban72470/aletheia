# Aletheia Implementation Plan

## Phase 1: Core Data Models (Task 1)
**Goal:** Implement Pydantic models matching JSON schemas

### 1.1 Shared Models (`sidecar/aletheia_sidecar/models/`)
- [x] `document.py` - Document, Page, Block, BoundingBox models
- [x] `query.py` - PerceptionQuery model
- [x] `diagram.py` - DiagramGraph, Node, Edge models
- [x] `provenance.py` - Provenance tracking model

### 1.2 Validation
- Schema validation against JSON schemas
- Type hints and runtime validation with Pydantic v2

---

## Phase 2: Sidecar API Endpoints (Task 2)
**Goal:** Create working FastAPI endpoints

### 2.1 Core Endpoints
- [ ] `POST /parse` - Parse document with file upload
- [ ] `POST /query` - Perception query against parsed document
- [ ] `GET /health` - Health check endpoint
- [ ] `GET /status/{document_id}` - Get parsing status

### 2.2 API Components
- [ ] Request/response models
- [ ] File upload handling with validation
- [ ] Error handling middleware
- [ ] CORS configuration

---

## Phase 3: Document Ingestion Pipeline (Task 3)
**Goal:** Build the document processing pipeline

### 3.1 Ingest Stage (`pipeline/ingest/`)
- [ ] `pdf_loader.py` - Load PDF using PyMuPDF
- [ ] `image_loader.py` - Load images (PNG, JPEG)
- [ ] `file_detector.py` - Auto-detect file type
- [ ] `metadata_extractor.py` - Extract basic metadata

### 3.2 Preprocess Stage (`pipeline/preprocess/`)
- [ ] `image_processor.py` - Normalize, resize, denoise
- [ ] `page_splitter.py` - Split multi-page documents
- [ ] `deskew.py` - Straighten skewed images

---

## Phase 4: OCR & Layout Analysis (Task 4)
**Goal:** Extract text and understand document structure

### 4.1 Layout Analysis (`pipeline/layout/`)
- [ ] `detector.py` - Detect blocks using LayoutParser
- [ ] `classifier.py` - Classify block types (heading, paragraph, table, figure)
- [ ] `reading_order.py` - Determine reading order

### 4.2 OCR Stage (`pipeline/ocr/`)
- [ ] `tesseract_engine.py` - Tesseract integration
- [ ] `text_extractor.py` - Extract text from images
- [ ] `confidence_scorer.py` - Score OCR confidence

### 4.3 Semantic Stage (`pipeline/semantic/`)
- [ ] `embeddings.py` - Generate embeddings (optional for basic)
- [ ] `chunker.py` - Chunk content for semantic search

---

## Phase 5: Storage Layer (Task 5)
**Goal:** Store and retrieve parsed documents

### 5.1 Local Storage (`storage/`)
- [ ] `file_store.py` - Store documents on disk
- [ ] `cache.py` - Cache parsed results
- [ ] `retrieval.py` - Query and retrieve documents

---

## Phase 6: CLI Commands (Task 6)
**Goal:** Functional CLI tool

### 6.1 Core Commands (`cli/aletheia_cli/commands/`)
- [ ] `parse_cmd.py` - Parse documents
- [ ] `query_cmd.py` - Query parsed documents
- [ ] `health_cmd.py` - Check sidecar health
- [ ] `config_cmd.py` - Configure CLI

### 6.2 Client (`cli/aletheia_cli/client/`)
- [ ] `sidecar_client.py` - HTTP client for sidecar API
- [ ] `error_handler.py` - Handle API errors gracefully

---

## Phase 7: VS Code Extension (Task 7)
**Goal:** Basic extension functionality

### 7.1 Commands (`extension/vscode/src/commands/`)
- [ ] `parseFile.ts` - Parse current file
- [ ] `preview.ts` - Preview parsed content
- [ ] `insertBlock.ts` - Insert extracted block

### 7.2 Integration
- [ ] `sidecar/client.ts` - API client
- [ ] `webview/renderer.ts` - Render parsed content

---

## Implementation Order

### Sprint 1: Foundations (Current)
1. Core data models ✓
2. Basic sidecar endpoints
3. Simple PDF/image ingestion

### Sprint 2: Processing
4. Layout detection
5. OCR integration
6. Basic storage

### Sprint 3: Integration
7. CLI commands
8. Extension commands
9. End-to-end testing

---

## Success Criteria

✅ **Minimal Demo Works:**
- Parse `examples/minimal_demo/sample.pdf`
- Extract text and structure
- Return JSON matching schema
- CLI can query sidecar
- Extension can preview document

✅ **Quality:**
- Type safety (mypy/TypeScript passes)
- Tests pass (>80% coverage)
- Linting passes
- Docker compose works

---

## Next Steps (Immediate)

1. **Implement Pydantic models** from JSON schemas
2. **Create basic FastAPI app** with health endpoint
3. **Add PDF loader** using PyMuPDF
4. **Wire up parse endpoint** to return mock data
5. **Test with curl/CLI**

Let's start coding! 🚀
