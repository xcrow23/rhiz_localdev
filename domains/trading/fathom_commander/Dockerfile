# Fathom Commander - Unified Trading Platform
# Orchestration layer for trading workflows

FROM python:3.11-slim

LABEL maintainer="Rhiz Partnership"
LABEL version="2.0.0"
LABEL description="Trading orchestration layer with MCP protocol"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency file
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir "qdrant-client[fastembed]>=1.7.0" "httpx>=0.27.0"

# Copy application code
COPY server.py ./
COPY gateway.py ./
COPY state.py ./
COPY config.yaml ./
COPY __init__.py ./
COPY auth.py ./
COPY tools/ ./tools/
COPY memory/ ./memory/

# Create directories for state and logs
RUN mkdir -p /app/state /app/logs

# Create non-root user for security
RUN useradd -m -u 1000 fc && \
    chown -R fc:fc /app
USER fc

# Environment variables (will be overridden by docker-compose)
ENV FATHOM_MCP_URL="http://fathom-mcp:8765"
ENV QDRANT_URL="http://qdrant:6333"
ENV FC_MODE="paper"
ENV FC_MAX_ORDER_USD="50"
ENV FC_APPROVAL_THRESHOLD_USD="20"
ENV FC_LOG_LEVEL="INFO"
ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=utf-8

# Expose MCP server port
EXPOSE 8766

# Note: No health check needed for stdio-based MCP server

# Run MCP server
CMD ["python", "-u", "server.py"]
