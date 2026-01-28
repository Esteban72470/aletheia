# Aletheia System Architecture

## Overview

Aletheia is a perceptual subsystem designed to bridge visual, spatial, and semi-structured knowledge into symbolic representations for AI coding assistants.

## Core Philosophy

> Current coding agents operate in a text-only, file-based epistemology, while real-world knowledge exists in visual, spatial, semi-structured, and analog formats.

## System Components

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Environment                          │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │  VS Code    │  │    CLI      │  │   Other Integrations    │  │
│  │  Extension  │  │  Interface  │  │   (Browser, JetBrains)  │  │
│  └──────┬──────┘  └──────┬──────┘  └───────────┬─────────────┘  │
│         │                │                      │                │
│         └────────────────┼──────────────────────┘                │
│                          │                                       │
│                          ▼                                       │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                    Local Sidecar Service                    │ │
│  │  ┌─────────────────────────────────────────────────────────┐│ │
│  │  │                   Parsing Pipeline                      ││ │
│  │  │  Ingest → Preprocess → Layout → OCR → Semantic → Post  ││ │
│  │  └─────────────────────────────────────────────────────────┘│ │
│  └─────────────────────────────────────────────────────────────┘ │
│                          │                                       │
│                          ▼                                       │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                    AI Agent Layer                           │ │
│  │           (GitHub Copilot, Antigravity, etc.)               │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Cognitive Pipeline Model

### 1. Perception Layer
- Raw sensory input (pixels, vector text, layout geometry)
- No reasoning, only observation
- Cached for re-processing

### 2. Spatial Reasoning Layer
- Reading order detection
- Semantic region identification
- Spatial relationship preservation

### 3. Symbol Grounding Layer
- Pixels → tokens
- Tables → relations
- Diagrams → graph representations

### 4. Semantic Compression Layer
- L0: Full OCR text (lossless)
- L1: Block-level summaries
- L2: Document-level semantic index
- L3: Task-oriented views

### 5. Agent Interface Layer
- Copilot: Plain text buffers
- Antigravity: Structured JSON
- CLI: Machine-readable schemas

## Design Principles

1. **Non-intrusive**: Zero repo pollution
2. **Composable**: Partial output consumption
3. **Explainable**: Traceable to source
4. **Agent-aligned**: Optimized for reasoning
