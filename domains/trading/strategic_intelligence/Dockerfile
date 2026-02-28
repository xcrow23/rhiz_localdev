# Strategic Intelligence Layer - Unified Trading Platform
# Intelligence and learning layer with Qdrant memory integration

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy SIL source code
COPY . .

# Create directories for runtime data and logs
RUN mkdir -p /app/data /app/logs

# Create non-root user for security
RUN useradd -m -u 1000 sil && \
    chown -R sil:sil /app
USER sil

# Environment variables (will be overridden by docker-compose)
ENV PYTHONUNBUFFERED=1
ENV QDRANT_HOST=qdrant
ENV QDRANT_PORT=6333
ENV SIL_ENABLE_MEMORY=true
ENV SIL_LEARNING_ENABLED=false
ENV SIL_LOG_LEVEL=INFO
ENV EMBEDDING_MODEL=all-MiniLM-L6-v2

# Expose API port
EXPOSE 8000

# Health check (uses unauthenticated /healthz endpoint for internal checks)
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/healthz || exit 1

# Run FastAPI server via uvicorn
CMD ["python", "-m", "uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "info"]
