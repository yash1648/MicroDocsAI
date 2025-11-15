# MicroDocs AI - Production Dockerfile
# Multi-stage build for optimized image size

# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

# Set metadata
LABEL maintainer="MicroDocs AI Team"
LABEL description="Context-Aware Documentation Generator for Spring Boot Microservices"
LABEL version="1.0.0"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    APP_HOME=/app

# Create non-root user for security
RUN useradd -m -u 1000 microdocs && \
    mkdir -p $APP_HOME && \
    chown -R microdocs:microdocs $APP_HOME

WORKDIR $APP_HOME

# Copy Python dependencies from builder
COPY --from=builder /root/.local /home/microdocs/.local

# Set PATH to include user Python packages
ENV PATH=/home/microdocs/.local/bin:$PATH

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy application code
COPY --chown=microdocs:microdocs . .

# Create necessary directories
RUN mkdir -p /app/logs /app/output /app/cache && \
    chown -R microdocs:microdocs /app/logs /app/output /app/cache

# Switch to non-root user
USER microdocs

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Expose port (for potential API server)
EXPOSE 8080

# Default command
CMD ["python3", "main.py"]

# Alternative entry points can be specified as:
# CMD ["python3", "rag_system.py"]
# CMD ["python3", "evaluation.py"]
