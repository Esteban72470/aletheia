# Debian Package Distribution

This directory contains resources for building Debian packages for Aletheia.

## Structure

```
deb/
├── DEBIAN/
│   ├── control         # Package metadata
│   ├── postinst        # Post-installation script
│   └── prerm           # Pre-removal script
├── usr/
│   └── local/
│       └── bin/
│           └── aletheia  # CLI binary
└── etc/
    └── aletheia/
        └── config.yaml   # Default configuration
```

## Building

```bash
make deb
```

## Installation

```bash
sudo dpkg -i aletheia_<version>_amd64.deb
sudo apt-get install -f  # Install dependencies
```

## Dependencies

- python3 (>= 3.10)
- tesseract-ocr
- poppler-utils
