# Aletheia Sidecar Dockerfile
# Multi-stage build for optimized production image

FROM python:3.10-slim as builder

WORKDIR /app

# Install system dependencies for document processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    tesseract-ocr \
    tesseract-ocr-eng \
    libtesseract-dev \
    poppler-utils \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY sidecar/pyproject.toml sidecar/poetry.lock* ./
RUN pip install --upgrade pip && \
    pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev --no-interaction --no-ansi

# Production stage
FROM python:3.10-slim as production

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-eng \
    poppler-utils \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY sidecar/ ./sidecar/
COPY shared_schemas/ ./shared_schemas/

# Create non-root user
RUN useradd -m -u 1000 aletheia && \
    chown -R aletheia:aletheia /app
USER aletheia

# Configure environment
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    ALETHEIA_LOG_LEVEL=INFO

EXPOSE 8420

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8420/health')"

# Run the sidecar
CMD ["python", "-m", "uvicorn", "sidecar.app.main:app", "--host", "0.0.0.0", "--port", "8420"]
