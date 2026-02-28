"""
Rhiz FastAPI Gateway - Mooncheck Ingestion & Vector Search

Standalone API service that:
1. Receives mooncheck data from Cloudflare Worker
2. Generates embeddings via local embedding service
3. Stores vectors in Qdrant
4. Provides semantic search capabilities

Architecture:
    Cloudflare Worker → FastAPI (this) → Embedding Service → Qdrant
"""

from fastapi import FastAPI, HTTPException, Query, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
import requests
import os
import logging
import uuid
import hashlib
from datetime import datetime
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Distance, VectorParams
from qdrant_client.http import models

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment configuration
EMBEDDING_SERVICE_URL = os.getenv("EMBEDDING_SERVICE_URL", "http://localhost:5000")
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "moonchecks")
API_KEY = os.getenv("RHIZ_API_KEY", None)  # Set in env for production

# Constants
MAX_TRANSCRIPT_LENGTH = 50000  # ~50KB max transcript
MAX_QUERY_LENGTH = 1000  # Max search query length

# Initialize FastAPI
app = FastAPI(
    title="Rhiz FastAPI Gateway",
    version="1.0.0",
    description="Mooncheck ingestion and vector search API"
)

# CORS middleware for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Qdrant client
qdrant_client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

# Helper functions
def verify_api_key(x_api_key: Optional[str] = Header(None)):
    """Verify API key if configured"""
    if API_KEY:  # Only require key if configured
        if not x_api_key or x_api_key != API_KEY:
            raise HTTPException(
                status_code=401,
                detail="Invalid or missing API key"
            )


# Pydantic models
class MooncheckRequest(BaseModel):
    transcript: str = Field(..., min_length=1, max_length=MAX_TRANSCRIPT_LENGTH, description="The mooncheck transcript text")
    topic_hint: str = Field(..., min_length=1, max_length=200, description="Topic or category hint")
    category: str = Field(default="blog", max_length=100, description="Content category")

    @validator('transcript', 'topic_hint')
    def strip_whitespace(cls, v):
        return v.strip()


class MooncheckResponse(BaseModel):
    success: bool
    mooncheck_id: int
    timestamp: str
    message: Optional[str] = None


class EmbedRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=MAX_TRANSCRIPT_LENGTH, description="Text to embed")


class EmbedResponse(BaseModel):
    embedding: List[float]
    dimension: int
    model: str


class SearchResult(BaseModel):
    id: int
    score: float
    payload: Dict[str, Any]


class SearchResponse(BaseModel):
    results: List[SearchResult]
    count: int


class HealthResponse(BaseModel):
    status: str
    services: Dict[str, str]
    timestamp: str


def ensure_collection_exists():
    """Ensure the moonchecks collection exists in Qdrant"""
    try:
        collections = qdrant_client.get_collections().collections
        collection_names = [c.name for c in collections]

        if QDRANT_COLLECTION not in collection_names:
            logger.info(f"Creating collection: {QDRANT_COLLECTION}")
            qdrant_client.create_collection(
                collection_name=QDRANT_COLLECTION,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE)
            )
            logger.info(f"Collection {QDRANT_COLLECTION} created successfully")
        else:
            logger.info(f"Collection {QDRANT_COLLECTION} already exists")

    except Exception as e:
        logger.error(f"Error ensuring collection exists: {e}")
        raise


def get_embedding(text: str) -> List[float]:
    """Generate embedding via embedding service"""
    try:
        response = requests.post(
            f"{EMBEDDING_SERVICE_URL}/embed",
            json={"text": text},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        return data["embedding"]
    except Exception as e:
        logger.error(f"Embedding service error: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"Embedding service unavailable: {str(e)}"
        )


def check_service_health(url: str, endpoint: str = "/health") -> str:
    """Check if a service is healthy"""
    try:
        response = requests.get(f"{url}{endpoint}", timeout=5)
        if response.status_code == 200:
            return "healthy"
        return f"unhealthy (status: {response.status_code})"
    except Exception as e:
        return f"unreachable ({str(e)})"


# API Endpoints
@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint with API info"""
    return {
        "service": "Rhiz FastAPI Gateway",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "mooncheck_ingest": "POST /mooncheck/ingest",
            "mooncheck_search": "GET /mooncheck/search",
            "embed": "POST /embed"
        }
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Multi-service health check"""

    # Check embedding service
    embedding_status = check_service_health(EMBEDDING_SERVICE_URL)

    # Check Qdrant
    try:
        qdrant_client.get_collections()
        qdrant_status = "healthy"
    except Exception as e:
        qdrant_status = f"unhealthy ({str(e)})"

    # Determine overall status
    overall_status = "healthy" if all([
        embedding_status == "healthy",
        qdrant_status == "healthy"
    ]) else "degraded"

    return HealthResponse(
        status=overall_status,
        services={
            "embedding_service": embedding_status,
            "qdrant": qdrant_status,
            "fastapi": "healthy"
        },
        timestamp=datetime.utcnow().isoformat()
    )


@app.post("/embed", response_model=EmbedResponse)
async def embed_text(request: EmbedRequest):
    """Generate embedding for text (proxy to embedding service)"""
    try:
        response = requests.post(
            f"{EMBEDDING_SERVICE_URL}/embed",
            json={"text": request.text},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()

        return EmbedResponse(
            embedding=data["embedding"],
            dimension=data["dimension"],
            model=data.get("model", "unknown")
        )
    except requests.exceptions.RequestException as e:
        logger.error(f"Embedding service error: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"Embedding service error: {str(e)}"
        )


@app.post("/mooncheck/ingest", response_model=MooncheckResponse, dependencies=[])
async def ingest_mooncheck(
    request: MooncheckRequest,
    x_api_key: Optional[str] = Header(None)
):
    """
    Ingest a mooncheck: generate embedding and store in Qdrant

    Flow:
    1. Receive transcript, topic_hint, category
    2. Generate embedding via embedding service
    3. Create Qdrant point with vector + metadata
    4. Return success with point ID and timestamp

    Requires API key if RHIZ_API_KEY environment variable is set.
    """

    # Verify API key if configured
    verify_api_key(x_api_key)

    try:
        # Ensure collection exists
        ensure_collection_exists()

        # Generate embedding
        logger.info(f"Generating embedding for mooncheck (topic: {request.topic_hint})")
        embedding = get_embedding(request.transcript)

        # Generate unique point ID using UUID (collision-resistant)
        # Convert UUID to 64-bit integer for Qdrant compatibility
        point_id = uuid.uuid4().int & ((1 << 64) - 1)
        timestamp_iso = datetime.utcnow().isoformat() + "Z"

        # Calculate word count
        word_count = len(request.transcript.split())

        # Create payload
        payload = {
            "transcript": request.transcript,
            "topic_hint": request.topic_hint,
            "category": request.category,
            "timestamp": timestamp_iso,
            "word_count": word_count,
            "created_via": "cloudflare_worker",
            "status": "captured"
        }

        # Store in Qdrant
        logger.info(f"Storing point {point_id} in Qdrant collection {QDRANT_COLLECTION}")
        qdrant_client.upsert(
            collection_name=QDRANT_COLLECTION,
            points=[
                PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload=payload
                )
            ]
        )

        logger.info(f"Mooncheck {point_id} stored successfully")

        return MooncheckResponse(
            success=True,
            mooncheck_id=point_id,
            timestamp=timestamp_iso,
            message="Mooncheck captured and stored successfully"
        )

    except HTTPException:
        # Re-raise HTTP exceptions from helpers
        raise
    except Exception as e:
        logger.error(f"Error ingesting mooncheck: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to ingest mooncheck: {str(e)}"
        )


@app.get("/mooncheck/search", response_model=SearchResponse)
async def search_moonchecks(
    query: str = Query(..., min_length=1, max_length=MAX_QUERY_LENGTH, description="Search query text"),
    limit: int = Query(5, ge=1, le=50, description="Number of results to return")
):
    """
    Semantic search across moonchecks using vector similarity

    Args:
        query: Search query text
        limit: Maximum number of results (1-50)

    Returns:
        List of moonchecks ordered by semantic similarity
    """

    try:
        # Generate embedding for query
        logger.info(f"Searching moonchecks with query: {query[:50]}...")
        query_embedding = get_embedding(query)

        # Search Qdrant
        search_results = qdrant_client.search(
            collection_name=QDRANT_COLLECTION,
            query_vector=query_embedding,
            limit=limit
        )

        # Format results
        results = [
            SearchResult(
                id=int(hit.id),
                score=float(hit.score),
                payload=hit.payload
            )
            for hit in search_results
        ]

        logger.info(f"Found {len(results)} results for query")

        return SearchResponse(
            results=results,
            count=len(results)
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Search error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize service on startup"""
    logger.info("Rhiz FastAPI Gateway starting up...")
    logger.info(f"Embedding service URL: {EMBEDDING_SERVICE_URL}")
    logger.info(f"Qdrant host: {QDRANT_HOST}:{QDRANT_PORT}")
    logger.info(f"Qdrant collection: {QDRANT_COLLECTION}")

    # Ensure collection exists
    try:
        ensure_collection_exists()
    except Exception as e:
        logger.warning(f"Could not ensure collection exists at startup: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
