# Fathom MCP Server - Kraken Execution Layer
# Docker image for unified trading platform deployment

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY pyproject.toml ./

# Install Python dependencies
# Extract dependencies from pyproject.toml and install via pip
RUN pip install --no-cache-dir \
    "mcp>=1.0.0" \
    "httpx>=0.27.0" \
    "websockets>=12.0" \
    "qdrant-client[fastembed]>=1.7.0" \
    "pydantic>=2.0.0" \
    "pyyaml>=6.0" \
    "python-dotenv>=1.0.0"

# Copy application source
COPY src/ ./src/
COPY config/ ./config/

# Create directories for data and logs
RUN mkdir -p /app/data /app/logs

# Create non-root user for security
RUN useradd -m -u 1000 fathom && \
    chown -R fathom:fathom /app
USER fathom

# Expose MCP server port
EXPOSE 8765

# Note: No health check needed for stdio-based MCP server

# Run MCP server (as module to support relative imports)
CMD ["python", "-m", "src.server"]
