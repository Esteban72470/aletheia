# Aletheia

> A perceptual subsystem for developer agents -- bridging visual, spatial, and semi-structured knowledge into symbolic representations for AI coding assistants.

**Status:** Phase 1 Part 1 Complete - Layout Analysis Implemented
**Version:** 0.2.0
**Last Updated:** January 28, 2026

---

## Table of Contents

- [Overview](#overview)
- [Project Status](#project-status)
- [Architecture](#architecture)
- [Components](#components)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [API Reference](#api-reference)
- [Development Progress](#development-progress)
- [Documentation](#documentation)
- [License](#license)

---

## Overview

Aletheia is a non-intrusive document and image parser designed to work alongside AI coding agents like GitHub Copilot and Google Antigravity. It provides a local perception layer that transforms PDFs, images, diagrams, and scanned documents into structured, agent-consumable formats.

### Key Principles

- **Non-intrusive**: Zero repo pollution, uses virtual documents and user-level cache
- **Composable**: Agents can consume partial outputs (tables, figures, summaries)
- **Explainable**: Every extracted token traces back to source with confidence scores
- **Agent-aligned**: Output optimized for reasoning, not just human reading
- **Type-safe**: Full Pydantic v2 validation with comprehensive type hints
- **Extensible**: Modular pipeline architecture for custom processors

---

## Project Status

### Completed Phases

| Phase        | Part   | Description             | Status   |
| ------------ | ------ | ----------------------- | -------- |
| Fundamentals | Part 1 | Core Infrastructure     | Complete |
| Fundamentals | Part 2 | Storage and Testing     | Complete |
| Fundamentals | Part 3 | Integration and Cleanup | Complete |
| Phase 1      | Part 1 | Layout Analysis         | Complete |

### Current Capabilities

**Document Processing:**
- PDF parsing with PyMuPDF (text extraction, bounding boxes, metadata)
- Image OCR with Tesseract (confidence scores, word-level boxes)
- Layout detection with LayoutParser or heuristic fallback
- Block classification (heading, paragraph, list, table, figure, caption)
- Reading order calculation (top-to-bottom, left-to-right)
- Image preprocessing (denoising, deskewing, contrast enhancement)

**API and Infrastructure:**
- FastAPI server with OpenAPI documentation
- RESTful endpoints for parse, query, and health
- In-memory and filesystem document storage
- Click-based CLI with parse, query, and preview commands
- Comprehensive test suite (unit and integration)

### Upcoming Work

| Phase   | Part   | Description          | Status      |
| ------- | ------ | -------------------- | ----------- |
| Phase 1 | Part 2 | Table Detection      | Not Started |
| Phase 1 | Part 3 | Production Hardening | Not Started |
| Phase 1 | Part 4 | VS Code Extension    | Not Started |
| Phase 2 | -      | Advanced ML Models   | Planned     |

---

## Architecture

```
                    +-------------------+
                    |    VS Code Ext    |
                    |  (UI / Commands)  |
                    +---------+---------+
                              |
                              v
+-------------+     +---------+---------+     +-------------+
|   CLI Tool  |---->|   Local Sidecar   |<----|  AI Agents  |
| (aletheia)  |<----|  (FastAPI + ML)   |---->| (Copilot)   |
+-------------+     +---------+---------+     +-------------+
                              |
              +---------------+---------------+
              |               |               |
              v               v               v
        +-----------+   +-----------+   +-----------+
        |  Storage  |   |  Pipeline |   |   Models  |
        | (FS/Mem)  |   |  Stages   |   | (OCR/ML)  |
        +-----------+   +-----------+   +-----------+
```

### Pipeline Flow

```
Document Input
      |
      v
+-----+-----+
|  Ingest   |  Detect MIME type, load raw bytes
+-----------+
      |
      v
+-----------+
| PreProcess|  Image cleaning, deskewing, contrast
+-----------+
      |
      v
+-----------+
|  Layout   |  Detect blocks, regions, reading order  [NEW]
+-----------+
      |
      v
+-----------+
|    OCR    |  Text extraction with word boxes
+-----------+
      |
      v
+-----------+
|  Tables   |  Table detection and structure  [PLANNED]
+-----------+
      |
      v
+-----------+
| PostProc  |  Merge blocks, validate, finalize
+-----------+
      |
      v
   Document
    Output
```

---

## Components

### Sidecar Service (`sidecar/`)

The core perceptual daemon providing document processing capabilities.

**Structure:**
```
sidecar/
  app/
    api/           REST API endpoints
      health.py      Health and readiness checks
      parse.py       Document parsing endpoint
      query.py       Document search endpoint
      models.py      Request/response schemas
    models/        Pydantic data models
      document.py    Document, Page, Block models
      diagram.py     Diagram and node models
      query.py       Query and search models
    pipeline/      Processing pipeline
      controller.py  High-level orchestration
      orchestrator.py Pipeline stage coordination
      ingest/        Document loaders (PDF, Image)
      preprocess/    Image cleaning and enhancement
      layout/        Layout detection backends
      ocr/           OCR backends (Tesseract, TrOCR)
      postprocess/   Block merging and validation
    storage/       Document persistence
      base.py        Storage interface
      memory.py      In-memory store
      filesystem.py  File-based store
    config.py      Configuration management
    logging.py     Logging setup
    main.py        FastAPI application
  scripts/
    benchmark.py     Performance measurement
    download_models.py Model downloading
    warmup.py        Model preloading
  tests/
    unit/          Unit tests
    integration/   Integration tests
    phase1/        Phase verification tests
```

### CLI Tool (`cli/`)

Command-line interface for interacting with Aletheia.

**Commands:**
```
aletheia parse <file>    Parse a document
aletheia query <id>      Query a stored document
aletheia preview <file>  Generate text preview
aletheia serve           Start the sidecar server
aletheia health          Check service health
```

### VS Code Extension (`extension/`)

IDE integration for document preview and interaction (planned).

### Shared Schemas (`shared_schemas/`)

Language-agnostic JSON schemas for cross-component validation.

**Schemas:**
- `document.schema.json` - Document structure
- `diagramgraph.schema.json` - Diagram representation
- `provenance.schema.json` - Source tracking
- `perception_query.schema.json` - Query format

---

## Installation

### System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr poppler-utils
```

**macOS:**
```bash
brew install tesseract poppler
```

**Windows:**
```
# Install Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki
# Add to PATH: C:\Program Files\Tesseract-OCR
```

### Python Dependencies

**Sidecar:**
```bash
cd sidecar
pip install -r requirements.txt
```

**CLI:**
```bash
cd cli
pip install -e .
```

### Optional Dependencies

For GPU-accelerated layout detection:
```bash
pip install layoutparser
pip install "detectron2@git+https://github.com/facebookresearch/detectron2.git"
```

---

## Quick Start

### 1. Start the Sidecar Server

```bash
cd sidecar
uvicorn app.main:app --host 0.0.0.0 --port 8420 --reload
```

The API documentation is available at: `http://localhost:8420/docs`

### 2. Parse a Document

**Using curl:**
```bash
curl -X POST http://localhost:8420/api/v1/parse \
  -F "file=@document.pdf" \
  -F "extract_tables=true" \
  -F "extract_layout=true"
```

**Using the CLI:**
```bash
aletheia parse document.pdf --output json --tables --layout
```

**Using Python:**
```python
from sidecar.app.pipeline.controller import PipelineController

controller = PipelineController()

with open("document.pdf", "rb") as f:
    document = await controller.process(
        filename="document.pdf",
        content=f.read(),
        mime_type="application/pdf",
        options={"extract_tables": True, "extract_layout": True}
    )

print(f"Extracted {len(document.pages)} pages")
for page in document.pages:
    print(f"Page {page.page_number}: {len(page.blocks)} blocks")
    for block in page.blocks:
        print(f"  - {block.type}: {block.text[:50]}...")
```

### 3. Query a Document

```bash
# Search for content
curl -X POST http://localhost:8420/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"document_id": "doc-123", "query": "find all tables"}'

# Using CLI
aletheia query doc-123 "find all code snippets"
```

### 4. Check Health

```bash
curl http://localhost:8420/health

# Response:
# {
#   "status": "healthy",
#   "version": "0.2.0",
#   "models_loaded": ["tesseract", "layoutparser"]
# }
```

---

## API Reference

### Endpoints

| Method | Endpoint                 | Description          |
| ------ | ------------------------ | -------------------- |
| GET    | `/health`                | Service health check |
| GET    | `/ready`                 | Readiness probe      |
| POST   | `/api/v1/parse`          | Parse a document     |
| POST   | `/api/v1/query`          | Query a document     |
| GET    | `/api/v1/documents/{id}` | Get document by ID   |

### Parse Request

```json
POST /api/v1/parse
Content-Type: multipart/form-data

file: <binary>
extract_tables: true
extract_layout: true
extract_figures: true
ocr_engine: "tesseract"
```

### Parse Response

```json
{
  "id": "doc-abc123",
  "filename": "document.pdf",
  "mime_type": "application/pdf",
  "pages": [
    {
      "page_number": 1,
      "width": 612.0,
      "height": 792.0,
      "blocks": [
        {
          "id": "p1_b1",
          "type": "heading",
          "bbox": [72.0, 72.0, 540.0, 100.0],
          "text": "Document Title",
          "confidence": 0.95
        },
        {
          "id": "p1_b2",
          "type": "paragraph",
          "bbox": [72.0, 120.0, 540.0, 300.0],
          "text": "Document content...",
          "confidence": 0.92
        }
      ],
      "tables": [],
      "figures": []
    }
  ],
  "metadata": {
    "title": "Document Title",
    "author": "Author Name",
    "created": "2026-01-28T10:00:00Z"
  }
}
```

---

## Development Progress

### Fundamentals Phase (Complete)

**Part 1 - Core Infrastructure:**
- Pydantic v2 data models with full validation
- FastAPI application with OpenAPI documentation
- Pipeline orchestrator architecture
- PDF loader using PyMuPDF
- Image loader with PIL
- Tesseract OCR backend
- In-memory document store
- Configuration management
- CLI framework with Click

**Part 2 - Storage and Testing:**
- Filesystem document store with JSON persistence
- Query endpoint with keyword and regex search
- Comprehensive pytest unit tests
- Sample PDF generator for demos
- Test fixtures and conftest setup

**Part 3 - Integration and Cleanup:**
- Integration tests for parse and query flows
- Warmup script with actual model loading
- Benchmark script with performance measurement
- Model download script with HuggingFace support
- Image preprocessing (denoising, deskewing)
- CLI preview command
- Query relevance scoring
- Health endpoint with model tracking

### Phase 1 Part 1 - Layout Analysis (Complete)

**LayoutParser Backend:**
- Full implementation with Detectron2 integration
- PubLayNet pretrained model support
- Lazy model initialization for performance
- Graceful degradation when GPU unavailable

**Heuristic Fallback:**
- Projection profile analysis for region detection
- Horizontal and vertical line grouping
- Whitespace-based block segmentation
- Works without any ML dependencies

**Block Classification:**
- Heading detection (position and size heuristics)
- Paragraph identification
- List detection by indentation patterns
- Table region detection
- Figure region detection
- Header and footer identification

**Reading Order:**
- Two-pass algorithm (vertical then horizontal)
- Row grouping with configurable tolerance
- Multi-column document support
- Proper handling of complex layouts

**Orchestrator Integration:**
- Layout detection stage added to pipeline
- Layout blocks guide OCR processing
- Text assignment to detected regions
- Word box assignment for OCR results
- Table and figure extraction from layout

### Files Modified in Phase 1 Part 1

```
sidecar/app/pipeline/layout/
  layout_base.py           Updated LayoutBlock with defaults
  layoutparser_backend.py  Full implementation (~300 lines)
  __init__.py              Updated exports

sidecar/app/pipeline/
  orchestrator.py          Layout integration (~200 lines added)

sidecar/tests/
  unit/test_layout.py      Unit tests for layout module
  phase1/test_phase1_part1.py  Verification script

docs/development/
  phase1_part1_plan.md     Planning document
```

---

## Documentation

### Development Guides

| Document                                                                               | Description                     |
| -------------------------------------------------------------------------------------- | ------------------------------- |
| [QUICKSTART.md](QUICKSTART.md)                                                         | Quick start guide with examples |
| [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md)                                       | Detailed implementation roadmap |
| [docs/development/FUNDAMENTALS_COMPLETE.md](docs/development/FUNDAMENTALS_COMPLETE.md) | Fundamentals phase summary      |
| [docs/development/phase1_part1_plan.md](docs/development/phase1_part1_plan.md)         | Phase 1 Part 1 planning         |

### Architecture Documentation

| Document                                     | Description                     |
| -------------------------------------------- | ------------------------------- |
| [docs/architecture.md](docs/architecture.md) | System design and components    |
| [docs/api_contract.md](docs/api_contract.md) | REST API specifications         |
| [docs/cli.md](docs/cli.md)                   | Command-line interface guide    |
| [docs/extension.md](docs/extension.md)       | VS Code extension documentation |
| [docs/threat_model.md](docs/threat_model.md) | Security considerations         |

### Examples

| Example                                                | Description                |
| ------------------------------------------------------ | -------------------------- |
| [examples/minimal_demo/](examples/minimal_demo/)       | Basic usage demonstration  |
| [examples/invoices/](examples/invoices/)               | Invoice processing example |
| [examples/research_papers/](examples/research_papers/) | Academic paper parsing     |
| [examples/diagrams/](examples/diagrams/)               | Diagram extraction example |

---

## Running Tests

### Unit Tests

```bash
cd sidecar
pytest tests/unit/ -v
```

### Integration Tests

```bash
cd sidecar
pytest tests/integration/ -v
```

### Phase Verification

```bash
cd sidecar
python tests/phase1/test_phase1_part1.py
```

### All Tests

```bash
cd sidecar
pytest tests/ -v --cov=app --cov-report=term-missing
```

---

## Configuration

### Environment Variables

| Variable                | Default       | Description               |
| ----------------------- | ------------- | ------------------------- |
| `ALETHEIA_PORT`         | `8420`        | Server port               |
| `ALETHEIA_HOST`         | `0.0.0.0`     | Server host               |
| `ALETHEIA_LOG_LEVEL`    | `INFO`        | Logging level             |
| `ALETHEIA_STORAGE_PATH` | `~/.aletheia` | Storage directory         |
| `ALETHEIA_CACHE_TTL`    | `3600`        | Cache TTL in seconds      |
| `TESSERACT_CMD`         | `tesseract`   | Tesseract executable path |

### Configuration File

Create `~/.aletheia/config.yaml`:

```yaml
server:
  host: 0.0.0.0
  port: 8420
  workers: 4

storage:
  type: filesystem
  path: ~/.aletheia/documents

pipeline:
  ocr_engine: tesseract
  extract_layout: true
  extract_tables: true
  extract_figures: true

logging:
  level: INFO
  format: json
```

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Make your changes
4. Run tests (`pytest tests/ -v`)
5. Commit your changes (`git commit -am 'Add new feature'`)
6. Push to the branch (`git push origin feature/new-feature`)
7. Create a Pull Request

---

## License

MIT License - See [LICENSE](LICENSE) for details.
