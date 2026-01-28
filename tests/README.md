# Aletheia Tests

This directory contains the complete test suite for the Aletheia project.

## Structure

```
tests/
├── sidecar/              # Sidecar service tests
│   ├── unit/             # Unit tests for sidecar components
│   ├── integration/      # Integration tests for sidecar APIs
│   └── performance/      # Performance benchmarks
├── cli/                  # CLI tests
│   ├── unit/             # Unit tests for CLI commands
│   └── integration/      # Integration tests for CLI workflows
├── extension/            # VS Code extension tests
│   ├── unit/             # Unit tests for extension components
│   └── integration/      # Integration tests for extension features
└── fundamentals/         # Fundamental system tests
    └── test_fundamentals.py  # Core system verification tests
```

## Running Tests

### Run all tests
```bash
pytest tests/
```

### Run specific test category
```bash
pytest tests/sidecar/
pytest tests/cli/
pytest tests/extension/
pytest tests/fundamentals/
```

### Run with coverage
```bash
pytest tests/ --cov=sidecar --cov=cli --cov-report=html
```
