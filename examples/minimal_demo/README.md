# Minimal Demo

This directory contains a minimal working example of Aletheia.

## Quick Start

1. **Start the sidecar** (if not using Docker):
   ```bash
   cd ../../sidecar
   poetry run uvicorn aletheia_sidecar.app.main:app --port 8420
   ```

2. **Parse a document**:
   ```bash
   aletheia parse sample.pdf --output result.json
   ```

3. **View the result**:
   ```bash
   cat result.json | jq .
   ```

## Using Docker

```bash
# Start sidecar
docker-compose up -d sidecar

# Parse document
aletheia parse sample.pdf
```

## Using VS Code Extension

1. Open `sample.pdf` in VS Code
2. Run command: `Aletheia: Parse Current Document`
3. View extracted content in the preview panel

## Sample Files

- `sample.pdf` - Simple PDF document
- `sample.png` - Simple image with text
- `expected_output.json` - Expected parsing result

## API Example

```python
import requests

# Parse a document
with open('sample.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:8420/parse',
        files={'file': f}
    )
    result = response.json()
    print(result)
```
