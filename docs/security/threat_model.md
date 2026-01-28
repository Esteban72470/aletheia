# Aletheia Threat Model

## Overview

This document outlines the security and privacy considerations for Aletheia.

## Threat Categories

### 1. Data Privacy

**Threat**: Sensitive document content leaking to unauthorized parties.

**Mitigations**:
- All processing happens locally by default
- No cloud uploads without explicit consent
- Cached data encrypted at rest
- Configurable PII redaction

### 2. Local Storage Security

**Threat**: Cached parsed documents accessible to other applications.

**Mitigations**:
- User-level cache directory permissions
- Optional AES-256 encryption for cache
- Automatic cache expiration
- Manual purge command available

### 3. Sidecar Communication

**Threat**: Man-in-the-middle attacks on localhost communication.

**Mitigations**:
- Localhost-only binding by default
- Optional TLS for local connections
- Request authentication tokens
- Rate limiting

### 4. Malicious Documents

**Threat**: Crafted PDFs/images exploiting parsing libraries.

**Mitigations**:
- Sandboxed parsing environment
- Input validation and sanitization
- Memory limits on processing
- Regular dependency updates

### 5. Model Supply Chain

**Threat**: Compromised ML models introducing vulnerabilities.

**Mitigations**:
- Verified model checksums
- Official model sources only
- Offline model loading option
- Model integrity verification

## Privacy Guarantees

1. **Local-first**: All processing on user's machine
2. **No telemetry by default**: Opt-in analytics only
3. **No cloud dependency**: Works fully offline
4. **Transparent caching**: User controls all stored data

## Security Best Practices

1. Keep sidecar updated
2. Use encrypted cache for sensitive documents
3. Enable PII redaction for shared outputs
4. Regularly purge cache: `aletheia cache purge`
5. Review extension permissions

## Incident Response

For security issues, contact: security@aletheia.dev

## Audit Log

All parsing operations can be logged:
```yaml
logging:
  audit: true
  log_file: ~/.local/share/aletheia/audit.log
```
