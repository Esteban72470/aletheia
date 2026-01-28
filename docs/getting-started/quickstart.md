# 🚀 Aletheia - Quick Start Guide

## What Was Built

I've implemented the **core fundamentals** of the Aletheia project:

### ✅ Complete Components

1. **Data Models** (Pydantic)
   - Document, Page, Block structures
   - Query and response models
   - Diagram graph models
   - Full type safety and validation

2. **Sidecar API** (FastAPI)
   - `POST /api/v1/parse` - Parse PDFs/images
   - `GET /health` - Health check
   - File upload handling
   - Error handling

3. **Document Processing Pipeline**
   - **PDF parsing** with PyMuPDF (real implementation)
   - **Image OCR** with Tesseract (real implementation)
   - Text extraction with bounding boxes
   - Multi-page support

4. **Storage Layer**
   - In-memory document store
   - Save, retrieve, list, delete operations
   - Ready to swap for database

5. **CLI Tool** (Click)
   - Parse command with options
   - Query command
   - Health check
   - HTTP client for sidecar

6. **Testing & Documentation**
   - Test script to verify all components
   - Implementation plan
   - Summary documentation

---

## 🏃 Getting Started

### 1. Install Dependencies

```bash
# System dependencies (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install tesseract-ocr poppler-utils

# Or macOS
brew install tesseract poppler

# Python environment
cd sidecar
poetry install

# Or with pip
pip install fastapi uvicorn pydantic PyMuPDF Pillow pytesseract httpx
```

### 2. Test the Fundamentals

```bash
# Run test script
cd aletheia
python test_fundamentals.py
```

Expected output:
```
============================================================
Aletheia Fundamentals Test
============================================================

[1/7] Testing data models...
✓ All models imported successfully

[2/7] Testing Pydantic validation...
✓ Created block: test1, confidence: 0.95

[3/7] Testing pipeline controller...
✓ Pipeline controller initialized (version: 0.1.0)

[4/7] Testing document store...
✓ Document store initialized (count: 0)

[5/7] Testing FastAPI app...
✓ FastAPI app loaded: Aletheia Sidecar

[6/7] Testing CLI...
✓ CLI commands loaded

[7/7] Testing document creation...
✓ Created document: test-doc-1
  - Pages: 1
  - Blocks: 1
  - Processing time: 100ms
✓ Document stored and retrieved successfully

============================================================
✓ All fundamental tests passed!
============================================================
```

### 3. Start the Sidecar

```bash
cd sidecar
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8420 --reload
```

Visit: http://localhost:8420/docs for API documentation

### 4. Test with curl

```bash
# Health check
curl http://localhost:8420/health

# Parse a PDF (create a sample PDF first)
curl -X POST http://localhost:8420/api/v1/parse \
  -F "file=@document.pdf" \
  -F "extract_tables=true" \
  -F "ocr_enabled=true" \
  | jq .
```

### 5. Use the CLI

```bash
cd cli
pip install -e .

# Check CLI
aletheia --help

# Parse document
aletheia parse document.pdf --output json

# Check sidecar health
aletheia health
```

---

## 📁 Project Structure

```
aletheia/
├── sidecar/              # FastAPI backend
│   ├── app/
│   │   ├── models/       # ✅ Pydantic data models
│   │   ├── api/          # ✅ API endpoints
│   │   ├── pipeline/     # ✅ Processing pipeline
│   │   │   ├── controller.py  # Main orchestrator
│   │   │   └── ingest/   # PDF/image loaders
│   │   ├── storage/      # ✅ Document store
│   │   └── main.py       # ✅ FastAPI app
│   └── pyproject.toml
│
├── cli/                  # Command-line interface
│   ├── aletheia_cli/
│   │   ├── commands/     # ✅ CLI commands
│   │   ├── client/       # ✅ HTTP client
│   │   └── main.py       # ✅ CLI entry point
│   └── setup.py
│
├── extension/            # VS Code extension (scaffolded)
│   └── vscode/
│       ├── src/
│       └── package.json
│
├── shared_schemas/       # JSON schemas
├── docs/                 # Documentation
├── examples/             # Sample files
│
├── test_fundamentals.py  # ✅ Test script
├── IMPLEMENTATION_PLAN.md # Detailed plan
└── FUNDAMENTALS_SUMMARY.md # This summary
```

---

## 🔧 Configuration

### Sidecar Config

`sidecar/app/config.py`:
```python
settings.port = 8420
settings.host = "0.0.0.0"
settings.environment = "development"
```

### CLI Config

`~/.config/aletheia/config.yaml`:
```yaml
sidecar:
  host: 127.0.0.1
  port: 8420
  timeout: 30

output:
  format: json
  verbose: false
```

---

## 📝 Example Usage

### Python API

```python
import asyncio
from pathlib import Path
from sidecar.app.pipeline.controller import PipelineController
from sidecar.app.storage.document_store import DocumentStore

async def main():
    # Initialize
    controller = PipelineController()
    store = DocumentStore()

    # Read file
    with open("document.pdf", "rb") as f:
        content = f.read()

    # Process
    document = await controller.process(
        filename="document.pdf",
        content=content,
        mime_type="application/pdf",
        options={
            "extract_tables": True,
            "ocr_enabled": True,
        }
    )

    # Store
    store.save(document)

    # Display results
    print(f"Document ID: {document.document_id}")
    print(f"Pages: {len(document.pages)}")

    for page in document.pages:
        print(f"\nPage {page.page_number}:")
        for block in page.blocks:
            print(f"  [{block.type}] {block.content[:50]}...")

asyncio.run(main())
```

### REST API

```bash
# Parse PDF
curl -X POST http://localhost:8420/api/v1/parse \
  -H "Content-Type: multipart/form-data" \
  -F "file=@document.pdf" \
  -F "extract_tables=true"

# Get document
curl http://localhost:8420/documents/{document_id}

# List all documents
curl http://localhost:8420/documents

# Query document
curl -X POST http://localhost:8420/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": "doc-123",
    "query": "find all headings",
    "mode": "keyword",
    "max_results": 10
  }'
```

---

## 🧪 What to Test

1. **Parse a PDF with text**
   ```bash
   aletheia parse document.pdf
   ```

2. **Parse an image with OCR**
   ```bash
   aletheia parse screenshot.png --ocr-engine tesseract
   ```

3. **Query a document**
   ```bash
   aletheia query doc-123 "find tables"
   ```

4. **Start sidecar and check health**
   ```bash
   # Terminal 1
   cd sidecar && poetry run uvicorn app.main:app --port 8420

   # Terminal 2
   curl http://localhost:8420/health
   ```

---

## 🐛 Troubleshooting

### Import errors for pydantic, fastapi, etc.
```bash
cd sidecar
poetry install
# or
pip install -r requirements.txt
```

### Tesseract not found
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# macOS
brew install tesseract

# Windows
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
```

### PyMuPDF import errors
```bash
pip install PyMuPDF
```

### Port 8420 already in use
```bash
# Find process
lsof -i :8420

# Kill it
kill -9 <PID>

# Or use different port
uvicorn app.main:app --port 8421
```

---

## 📈 Next Steps

### Immediate Enhancements

1. **Add real PDF sample**
   - Place a PDF in `examples/minimal_demo/sample.pdf`
   - Test parsing: `aletheia parse examples/minimal_demo/sample.pdf`

2. **Implement proper tests**
   - `sidecar/tests/test_models.py`
   - `sidecar/tests/test_pipeline.py`
   - Run: `pytest tests/`

3. **Add database storage**
   - Replace in-memory store with PostgreSQL/MongoDB
   - Implement `storage/db_store.py`

### Advanced Features (Phase 2)

4. **Layout detection**
   - Integrate LayoutParser
   - Classify block types
   - Detect reading order

5. **Table extraction**
   - Detect table structure
   - Extract cells
   - Export to CSV

6. **Semantic search**
   - Generate embeddings
   - Vector storage
   - Similarity search

7. **VS Code extension**
   - Preview parsed documents
   - Inline parsing
   - Quick actions

---

## 📚 Documentation

- [Implementation Plan](../development/implementation_plan.md) - Detailed implementation roadmap
- [Fundamentals Summary](../development/fundamentals_summary.md) - Complete summary of what was built
- [README](../../README.md) - Main project README
- [System Architecture](../architecture/system_architecture.md) - System architecture
- [API Contract](../api/api_contract.md) - API specifications

---

## ✅ Verification Checklist

- [x] Data models defined with Pydantic
- [x] FastAPI app with health endpoint
- [x] PDF parsing with PyMuPDF
- [x] Image OCR with Tesseract
- [x] Document storage layer
- [x] CLI with parse command
- [x] HTTP client for sidecar
- [x] Test script passes
- [ ] Real PDF parsed successfully
- [ ] Docker Compose working
- [ ] Unit tests added
- [ ] Integration tests added

---

**Status:** ✅ Fundamentals Complete
**Ready for:** Testing with real documents and Phase 2 implementation
**Version:** 0.1.0
**Date:** January 28, 2026
