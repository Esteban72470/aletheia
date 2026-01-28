# Aletheia API Contract

## Overview

This document defines the REST API contract for the Aletheia sidecar service.

## Base URL

```
http://localhost:8420/api/v1
```

## Endpoints

### Health Check

```
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "uptime_seconds": 3600,
  "models_loaded": ["tesseract", "layoutparser"]
}
```

### Parse Document

```
POST /parse
Content-Type: multipart/form-data
```

**Request:**
- `file`: Document file (PDF, image)
- `options`: JSON configuration

**Options Schema:**
```json
{
  "pages": "1-5",
  "ocr_engine": "tesseract",
  "extract_tables": true,
  "extract_layout": true,
  "output_level": "L1"
}
```

**Response:**
```json
{
  "document_id": "abc123",
  "pages": [
    {
      "page_number": 1,
      "width": 612,
      "height": 792,
      "blocks": [
        {
          "id": "block_1",
          "type": "paragraph",
          "bbox": [72, 100, 540, 150],
          "text": "...",
          "confidence": 0.95
        }
      ],
      "tables": [],
      "figures": []
    }
  ],
  "metadata": {
    "total_pages": 5,
    "processing_time_ms": 1234
  }
}
```

### Query (Perception Query)

```
POST /query
Content-Type: application/json
```

**Request:**
```json
{
  "document_id": "abc123",
  "query": "Extract all invoice line items",
  "page_range": [1, 3],
  "output_format": "structured"
}
```

**Response:**
```json
{
  "query_id": "q123",
  "results": [...],
  "confidence": 0.89
}
```

## Error Responses

```json
{
  "error": {
    "code": "PARSE_ERROR",
    "message": "Failed to parse document",
    "details": "..."
  }
}
```

## Status Codes

| Code | Description           |
| ---- | --------------------- |
| 200  | Success               |
| 400  | Bad request           |
| 404  | Document not found    |
| 500  | Internal server error |
| 503  | Service unavailable   |
