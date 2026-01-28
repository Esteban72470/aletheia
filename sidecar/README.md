# Aletheia Sidecar

Local perceptual daemon for document and image parsing.

## Overview

The sidecar is a FastAPI-based microservice that handles all heavy document processing, including PDF parsing, OCR, layout detection, and semantic extraction.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload --port 8420

# Or use Docker
docker build -t aletheia-sidecar .
docker run -p 8420:8420 aletheia-sidecar
```

## API Endpoints

- `GET /health` - Health check
- `POST /parse` - Parse document
- `POST /query` - Query parsed document

## Architecture

```
app/
├── api/          # FastAPI routes
├── pipeline/     # Processing stages
├── storage/      # Cache and filesystem
└── utils/        # Helpers
```

## Configuration

Environment variables:
- `ALETHEIA_ENV`: development/production
- `ALETHEIA_LOG_LEVEL`: DEBUG/INFO/WARNING/ERROR
- `ALETHEIA_CACHE_DIR`: Cache directory path
- `ALETHEIA_MODELS_DIR`: Models directory path
