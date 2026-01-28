# Aletheia CLI

Command-line interface for the Aletheia document parser.

## Installation

```bash
pip install -e .
```

## Usage

```bash
# Parse a document
aletheia parse document.pdf

# Preview parsed output
aletheia preview document.pdf --output preview.html

# Extract specific elements
aletheia extract document.pdf --type tables

# Start sidecar service
aletheia serve --port 8420
```

## Commands

- `parse` - Parse documents and output structured data
- `preview` - Generate visual previews
- `extract` - Extract specific elements
- `serve` - Start the local sidecar service

See `aletheia --help` for full documentation.
