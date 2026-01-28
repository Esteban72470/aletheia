# Aletheia VS Code Extension

## Overview

The Aletheia VS Code extension provides seamless integration with the parsing sidecar, enabling document and image understanding directly in your editor.

## Features

- **Parse Documents**: Right-click any PDF/image to parse
- **Visual Preview**: See parsed output with bounding boxes
- **Insert Blocks**: Insert parsed content into editor
- **Virtual Documents**: Expose parsed content to Copilot without modifying files

## Installation

1. Install from VS Code Marketplace: `Aletheia`
2. Or install VSIX: `code --install-extension aletheia-x.x.x.vsix`

## Commands

| Command                   | Description           | Keybinding     |
| ------------------------- | --------------------- | -------------- |
| `Aletheia: Parse File`    | Parse selected file   | `Ctrl+Shift+P` |
| `Aletheia: Preview`       | Open visual preview   | `Ctrl+Shift+V` |
| `Aletheia: Insert Block`  | Insert selected block | -              |
| `Aletheia: Start Sidecar` | Start local sidecar   | -              |

## Configuration

```json
{
  "aletheia.sidecar.host": "127.0.0.1",
  "aletheia.sidecar.port": 8420,
  "aletheia.sidecar.autoStart": true,
  "aletheia.cache.enabled": true,
  "aletheia.preview.showOverlay": true,
  "aletheia.preview.theme": "auto"
}
```

## Architecture

```
┌─────────────────────────────────────────┐
│           VS Code Extension             │
├─────────────────────────────────────────┤
│  Commands  │  Webview  │  Virtual FS    │
├─────────────────────────────────────────┤
│          Sidecar Client                 │
├─────────────────────────────────────────┤
│          Local Sidecar (HTTP)           │
└─────────────────────────────────────────┘
```

## Usage with Copilot

1. Parse a document using `Aletheia: Parse File`
2. The parsed content opens in a virtual buffer
3. Copilot can now reference this content for completions
4. Close the buffer when done (no files are modified)

## Troubleshooting

### Sidecar not connecting
- Ensure sidecar is running: `aletheia serve`
- Check port availability: default 8420

### Slow parsing
- Enable caching in settings
- Reduce page range for large documents
