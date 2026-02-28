"""
Unified Trading Platform API Gateway
Routes requests to Fathom (execution), FC (orchestration), and SIL (intelligence)

Architecture:
    Client → Gateway (8080) → {
        Fathom MCP (8765) - Kraken execution layer
        Fathom Commander (8766) - Orchestration layer
        SIL FastAPI (8000) - Intelligence layer
        Qdrant (6333) - Shared memory
    }
"""

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx
import os
import logging
from typing import Optional, Dict, Any

# Configure logging
logging.basicConfig(
    level=os.getenv("GATEWAY_LOG_LEVEL", "INFO"),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Environment configuration
FATHOM_URL = os.getenv("FATHOM_URL", "http://fathom-mcp:8765")
FC_URL = os.getenv("FC_URL", "http://fathom-commander:8766")
SIL_URL = os.getenv("SIL_URL", "http://sil-fastapi:8000")
QDRANT_URL = os.getenv("QDRANT_URL", "http://qdrant:6333")

# Health check authentication (required - no default for security)
HEALTH_CHECK_KEY = os.getenv("HEALTH_CHECK_KEY")
if not HEALTH_CHECK_KEY:
    raise ValueError("HEALTH_CHECK_KEY environment variable is required for health check authentication")

# Initialize FastAPI
app = FastAPI(
    title="Unified Trading Platform Gateway",
    version="1.0.0",
    description="Routes requests to Fathom, FC, and SIL services"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# HTTP client with timeouts
client = httpx.AsyncClient(timeout=30.0)


@app.on_event("shutdown")
async def shutdown_event():
    """Close HTTP client on shutdown"""
    await client.aclose()


@app.get("/health")
async def health_check(request: Request):
    """
    Aggregate health check across all services
    Requires X-Health-Check-Key header for authentication
    """
    # Verify health check authentication
    auth_key = request.headers.get("X-Health-Check-Key")
    if auth_key != HEALTH_CHECK_KEY:
        return JSONResponse(
            content={"error": "Forbidden", "message": "Invalid or missing X-Health-Check-Key header"},
            status_code=403
        )

    services = {
        "fathom": FATHOM_URL,
        "fc": FC_URL,
        "sil": SIL_URL,
        "qdrant": QDRANT_URL
    }

    health_status = {
        "gateway": "healthy",
        "services": {}
    }

    all_healthy = True

    for service_name, service_url in services.items():
        try:
            # Try /health endpoint first, fall back to base URL
            health_endpoint = f"{service_url}/health" if service_name != "qdrant" else f"{service_url}/healthz"
            response = await client.get(health_endpoint, timeout=5.0)

            health_status["services"][service_name] = {
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "response_code": response.status_code
            }

            if response.status_code != 200:
                all_healthy = False

        except Exception as e:
            health_status["services"][service_name] = {
                "status": "unreachable",
                "error": str(e)
            }
            all_healthy = False

    health_status["overall"] = "healthy" if all_healthy else "degraded"

    return JSONResponse(
        content=health_status,
        status_code=200 if all_healthy else 503
    )


# ========================================
# FATHOM ROUTES (Execution Layer)
# ========================================

@app.api_route("/fathom/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_fathom(path: str, request: Request):
    """
    Proxy all /fathom/* requests to Fathom MCP server
    """
    try:
        # Forward request to Fathom
        url = f"{FATHOM_URL}/{path}"
        headers = dict(request.headers)
        body = await request.body()

        response = await client.request(
            method=request.method,
            url=url,
            headers=headers,
            content=body
        )

        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers)
        )

    except Exception as e:
        logger.error(f"Fathom proxy error: {e}")
        raise HTTPException(status_code=502, detail=f"Fathom service error: {str(e)}")


# ========================================
# FATHOM COMMANDER ROUTES (Orchestration)
# ========================================

@app.api_route("/fc/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_fc(path: str, request: Request):
    """
    Proxy all /fc/* requests to Fathom Commander
    """
    try:
        url = f"{FC_URL}/{path}"
        headers = dict(request.headers)
        body = await request.body()

        response = await client.request(
            method=request.method,
            url=url,
            headers=headers,
            content=body
        )

        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers)
        )

    except Exception as e:
        logger.error(f"FC proxy error: {e}")
        raise HTTPException(status_code=502, detail=f"FC service error: {str(e)}")


# ========================================
# SIL ROUTES (Intelligence Layer)
# ========================================

@app.api_route("/sil/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_sil(path: str, request: Request):
    """
    Proxy all /sil/* requests to Strategic Intelligence Layer
    """
    try:
        url = f"{SIL_URL}/{path}"
        headers = dict(request.headers)
        body = await request.body()

        response = await client.request(
            method=request.method,
            url=url,
            headers=headers,
            content=body
        )

        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers)
        )

    except Exception as e:
        logger.error(f"SIL proxy error: {e}")
        raise HTTPException(status_code=502, detail=f"SIL service error: {str(e)}")


# ========================================
# QDRANT ROUTES (Shared Memory)
# ========================================

@app.api_route("/qdrant/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_qdrant(path: str, request: Request):
    """
    Proxy all /qdrant/* requests to Qdrant vector database
    """
    try:
        url = f"{QDRANT_URL}/{path}"
        headers = dict(request.headers)
        body = await request.body()

        response = await client.request(
            method=request.method,
            url=url,
            headers=headers,
            content=body
        )

        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers)
        )

    except Exception as e:
        logger.error(f"Qdrant proxy error: {e}")
        raise HTTPException(status_code=502, detail=f"Qdrant service error: {str(e)}")


# ========================================
# CONVENIENCE ROUTES
# ========================================

@app.get("/")
async def root():
    """
    Gateway info endpoint
    """
    return {
        "service": "Unified Trading Platform Gateway",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "fathom": "/fathom/*",
            "fc": "/fc/*",
            "sil": "/sil/*",
            "qdrant": "/qdrant/*"
        },
        "services": {
            "fathom": FATHOM_URL,
            "fc": FC_URL,
            "sil": SIL_URL,
            "qdrant": QDRANT_URL
        }
    }


@app.get("/status")
async def status(request: Request):
    """
    Quick status check (alias for /health)
    Requires X-Health-Check-Key header for authentication
    """
    return await health_check(request)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info")
