# Aletheia CLI Documentation

## Overview

The Aletheia CLI provides command-line access to document parsing and extraction capabilities.

## Installation

```bash
pip install aletheia-cli
# or
pip install -e cli/
```

## Commands

### Parse

Parse a document and output structured data.

```bash
aletheia parse <file> [options]

Options:
  --output, -o      Output format (json, markdown, text)
  --pages           Page range to process (e.g., "1-5", "1,3,5")
  --ocr-engine      OCR engine to use (tesseract, trocr, easyocr)
  --layout          Enable layout detection
  --tables          Extract tables
  --cache           Use cached results if available
```

### Preview

Generate a visual preview of parsed output.

```bash
aletheia preview <file> [options]

Options:
  --output, -o      Output file path
  --format          Preview format (html, svg, png)
  --overlay         Show bounding box overlay
```

### Extract

Extract specific elements from documents.

```bash
aletheia extract <file> [options]

Options:
  --type, -t        Element type (tables, figures, text, all)
  --output, -o      Output directory
  --format          Output format per element type
```

### Serve

Start the local sidecar service.

```bash
aletheia serve [options]

Options:
  --port, -p        Port number (default: 8420)
  --host            Host address (default: 127.0.0.1)
  --workers         Number of worker processes
  --reload          Enable auto-reload for development
```

## Configuration

Configuration file: `~/.config/aletheia/config.yaml`

```yaml
sidecar:
  host: 127.0.0.1
  port: 8420
  timeout: 30

cache:
  enabled: true
  directory: ~/.cache/aletheia
  max_size_gb: 10

defaults:
  ocr_engine: tesseract
  output_format: json
```

## Exit Codes

| Code | Description      |
| ---- | ---------------- |
| 0    | Success          |
| 1    | General error    |
| 2    | File not found   |
| 3    | Parse error      |
| 4    | Connection error |
