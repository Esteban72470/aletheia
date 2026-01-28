# Aletheia CLI Dockerfile
# Lightweight image for CLI distribution

FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install CLI
COPY cli/ ./cli/
COPY shared_schemas/ ./shared_schemas/

RUN pip install --upgrade pip && \
    pip install ./cli/

# Create non-root user
RUN useradd -m -u 1000 aletheia && \
    chown -R aletheia:aletheia /app
USER aletheia

ENTRYPOINT ["aletheia"]
CMD ["--help"]
