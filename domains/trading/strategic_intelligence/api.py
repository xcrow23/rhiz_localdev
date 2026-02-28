"""
Strategic Intelligence Layer - HTTP API

FastAPI wrapper for SIL orchestrator providing REST endpoints for:
- Health checks
- Regime classification queries
- Strategy selection
- Trade decision processing

Designed for n8n workflow integration and cloud deployment.
"""

from fastapi import FastAPI, HTTPException, Body, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
import logging
import os
from pathlib import Path

from sil_orchestrator import SILOrchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Health check authentication (required - no default for security)
HEALTH_CHECK_KEY = os.getenv("HEALTH_CHECK_KEY")
if not HEALTH_CHECK_KEY:
    raise ValueError("HEALTH_CHECK_KEY environment variable is required for health check authentication")

# Initialize FastAPI app
app = FastAPI(
    title="Strategic Intelligence Layer API",
    version="1.0.0",
    description="AI-powered trading intelligence for regime-aware strategy selection"
)

# Initialize SIL orchestrator (singleton)
sil_orchestrator = None

def get_orchestrator() -> SILOrchestrator:
    """Get or initialize SIL orchestrator singleton."""
    global sil_orchestrator
    if sil_orchestrator is None:
        # Read Qdrant configuration from environment
        qdrant_mode = os.getenv("QDRANT_MODE", "server")
        qdrant_host = os.getenv("QDRANT_HOST", "localhost")
        qdrant_port = int(os.getenv("QDRANT_PORT", "6333"))
        qdrant_path = os.getenv("QDRANT_PATH", "./data/qdrant")
        enable_memory = os.getenv("SIL_ENABLE_MEMORY", "false").lower() == "true"

        logger.info(f"Initializing SIL with Qdrant mode: {qdrant_mode}")

        sil_orchestrator = SILOrchestrator(
            qdrant_mode=qdrant_mode,
            qdrant_host=qdrant_host,
            qdrant_port=qdrant_port,
            qdrant_path=qdrant_path,
            enable_memory=enable_memory,
            enable_learning=False,  # Phase 2.5
            enable_transparency=True
        )
        logger.info("SIL Orchestrator initialized")
    return sil_orchestrator


# ========================================
# Request/Response Models
# ========================================

class OHLCVData(BaseModel):
    """OHLCV candle data."""
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float

class TradeDecisionRequest(BaseModel):
    """Request for trade decision."""
    pair: str = Field(..., example="BTC/USD", description="Trading pair (BTC/USD, ETH/USD, SOL/USD)")
    ohlcv: List[OHLCVData] = Field(..., description="OHLCV data (200+ candles required)")
    portfolio_balance: float = Field(..., example=100.0, description="Current portfolio balance in USD")
    current_position: Optional[float] = Field(0.0, description="Current position size (0 if no position)")

class RegimeQueryRequest(BaseModel):
    """Request for regime classification."""
    pair: str = Field(..., example="BTC/USD")
    ohlcv: List[OHLCVData] = Field(..., description="OHLCV data (200+ candles)")

class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    components: Dict[str, str]

class RefreshRegimesRequest(BaseModel):
    """Request for regime refresh."""
    pairs: List[str] = Field(..., example=["BTC/USD", "ETH/USD"], description="Trading pairs to refresh")
    full_refresh: bool = Field(False, description="Whether to force full refresh vs cached data")


# ========================================
# API Endpoints
# ========================================

@app.get("/", response_model=HealthResponse)
async def root(request: Request):
    """Root endpoint - health check."""
    return await health_check(request)

@app.get("/healthz")
async def healthz():
    """
    Internal health check endpoint for Docker healthcheck.

    Does not require authentication - used only by Docker HEALTHCHECK command.
    For external health checks with component details, use /health with X-Health-Check-Key.
    """
    try:
        # Quick check - just verify we can import and initialize
        orchestrator = get_orchestrator()
        return {"status": "healthy"}
    except Exception as e:
        logger.error(f"Internal health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

@app.get("/health", response_model=HealthResponse)
async def health_check(request: Request):
    """
    Health check endpoint.

    Requires X-Health-Check-Key header for authentication.

    Returns service status and component availability.
    """
    # Verify health check authentication
    auth_key = request.headers.get("X-Health-Check-Key")
    if auth_key != HEALTH_CHECK_KEY:
        raise HTTPException(
            status_code=403,
            detail="Invalid or missing X-Health-Check-Key header"
        )

    try:
        orchestrator = get_orchestrator()

        # Check components
        components = {
            "market_context": "operational",
            "strategy_selector": "operational",
            "position_sizer": "operational",
            "memory": "operational" if orchestrator.memory_client else "disabled",
            "learning": "operational" if orchestrator.learning_engine else "disabled"
        }

        return HealthResponse(
            status="healthy",
            version="1.0.0",
            components=components
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")


@app.post("/regime/classify")
async def classify_regime(request: RegimeQueryRequest):
    """
    Classify current market regime for a trading pair.

    Args:
        request: Regime classification request with OHLCV data

    Returns:
        Current regime classification with confidence score
    """
    try:
        orchestrator = get_orchestrator()

        # Convert OHLCV data to DataFrame format
        import pandas as pd
        ohlcv_df = pd.DataFrame([
            {
                'timestamp': candle.timestamp,
                'open': candle.open,
                'high': candle.high,
                'low': candle.low,
                'close': candle.close,
                'volume': candle.volume
            }
            for candle in request.ohlcv
        ])

        if len(ohlcv_df) < 30:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient data: need 30+ candles, got {len(ohlcv_df)}"
            )

        # Get market context
        context = orchestrator.market_context_engine.analyze(
            ohlcv=ohlcv_df
        )

        return {
            "pair": request.pair,
            "regime": context.regime,
            "confidence": context.regime_confidence,
            "volatility_regime": context.volatility_regime,
            "volatility_level": context.volatility_level,
            "sentiment_direction": context.sentiment_direction,
            "data_quality": context.data_quality,
            "candles_analyzed": len(ohlcv_df),
            "timestamp": datetime.utcnow().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Regime classification failed: {e}")
        raise HTTPException(status_code=500, detail=f"Classification error: {str(e)}")


@app.post("/strategy/select")
async def select_strategy(request: TradeDecisionRequest):
    """
    Get trade decision from SIL orchestrator.

    Args:
        request: Trade decision request with OHLCV and portfolio data

    Returns:
        SIL decision with strategy, action, position size, confidence
    """
    try:
        orchestrator = get_orchestrator()

        # Convert OHLCV data to DataFrame
        import pandas as pd
        ohlcv_df = pd.DataFrame([
            {
                'timestamp': candle.timestamp,
                'open': candle.open,
                'high': candle.high,
                'low': candle.low,
                'close': candle.close,
                'volume': candle.volume
            }
            for candle in request.ohlcv
        ])

        if len(ohlcv_df) < 30:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient data: need 30+ candles, got {len(ohlcv_df)}"
            )

        # Get current price from latest candle
        current_price = float(ohlcv_df.iloc[-1]['close'])

        # Build portfolio state
        portfolio_state = {
            "total_value": float(request.portfolio_balance),
            "exposure": float(request.current_position or 0),
            "positions": {}
        }

        # Get SIL decision
        decision = orchestrator.analyze_and_decide(
            ohlcv_data=ohlcv_df,
            current_price=current_price,
            portfolio_state=portfolio_state
        )

        # Convert to JSON-serializable format
        # Extract market context fields
        market_context = decision.market_context

        return {
            "pair": request.pair,
            "regime": market_context.get("regime"),
            "regime_confidence": market_context.get("regime_confidence"),
            "volatility_regime": market_context.get("volatility_regime"),
            "selected_strategy": decision.strategy_name,
            "action": decision.action,
            "position_size_usd": decision.position.get("amount_usd", 0) if decision.position else 0,
            "position_size_asset": decision.position.get("amount_asset", 0) if decision.position else 0,
            "confidence": decision.confidence,
            "reasoning": decision.reasoning,
            "risk_check": decision.risk_check,
            "trace_factors": decision.trace_factors,
            "timestamp": decision.timestamp.isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Strategy selection failed: {e}")
        raise HTTPException(status_code=500, detail=f"Selection error: {str(e)}")


@app.get("/config/strategies")
async def get_strategies():
    """
    Get available strategies and their configurations.

    Returns:
        List of strategies with regime preferences and parameters
    """
    try:
        orchestrator = get_orchestrator()

        # Get strategy configs for all assets
        strategies = {}
        for asset in ["BTC", "ETH", "SOL"]:
            pair = f"{asset}/USD"
            config = orchestrator.strategy_selector.config.get(pair.replace("/", ""), {})
            strategies[pair] = {
                "strategies": list(config.get("strategies", {}).keys()),
                "global_settings": config.get("global_settings", {})
            }

        return strategies

    except Exception as e:
        logger.error(f"Strategy config retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Config error: {str(e)}")


@app.post("/refresh_regimes")
async def refresh_regimes(request: RefreshRegimesRequest):
    """
    Refresh market regime classifications for specified pairs.

    This endpoint fetches current OHLCV data from FC Gateway and
    classifies regimes for each pair. Used by strategy-refresh worker
    to keep regime classifications current.

    Args:
        request: Refresh request with pairs and full_refresh flag

    Returns:
        Regime classifications for each pair with confidence scores
    """
    try:
        import requests
        import pandas as pd
        from datetime import datetime, timedelta

        # FC Gateway configuration
        fc_gateway_url = os.getenv("FC_GATEWAY_URL", "http://fc-http-gateway:8767")
        fc_api_key = os.getenv("FC_HTTP_API_KEY")

        if not fc_api_key:
            raise HTTPException(
                status_code=503,
                detail="FC_HTTP_API_KEY not configured - cannot fetch OHLCV data"
            )

        orchestrator = get_orchestrator()
        results = []

        for pair in request.pairs:
            try:
                # Convert pair format: "BTC/USD" → "XXBTZUSD" for Kraken
                kraken_pair = pair.replace("BTC/USD", "XXBTZUSD").replace("ETH/USD", "XETHZUSD")

                # Fetch OHLCV data from FC Gateway
                ohlcv_endpoint = f"{fc_gateway_url}/market/ohlc?pair={kraken_pair}&interval=5"
                headers = {"Authorization": f"Bearer {fc_api_key}"}

                logger.info(f"Fetching OHLCV for {pair} from FC Gateway...")
                response = requests.get(ohlcv_endpoint, headers=headers, timeout=10)

                if response.status_code != 200:
                    logger.error(f"FC Gateway returned {response.status_code} for {pair}")
                    results.append({
                        "pair": pair,
                        "success": False,
                        "error": f"Failed to fetch OHLCV: HTTP {response.status_code}"
                    })
                    continue

                ohlcv_data = response.json()

                # Check if FC returned success
                if not ohlcv_data.get("success"):
                    logger.error(f"FC Gateway error for {pair}: {ohlcv_data.get('error')}")
                    results.append({
                        "pair": pair,
                        "success": False,
                        "error": ohlcv_data.get("error", "Unknown error from FC Gateway")
                    })
                    continue

                # Convert to DataFrame
                # FC Gateway format: {"success": true, "candles": [{time, open, high, low, close, volume, ...}]}
                candles = ohlcv_data.get("candles", [])

                # Note: FC Gateway currently returns ~50 candles by default (Kraken API limitation)
                # This is sufficient for basic regime classification, though 200+ would be ideal
                if len(candles) < 30:
                    results.append({
                        "pair": pair,
                        "success": False,
                        "error": f"Insufficient data: got {len(candles)} candles, need at least 30"
                    })
                    continue

                ohlcv_df = pd.DataFrame([
                    {
                        'timestamp': datetime.fromtimestamp(candle['time']),
                        'open': float(candle['open']),
                        'high': float(candle['high']),
                        'low': float(candle['low']),
                        'close': float(candle['close']),
                        'volume': float(candle['volume'])
                    }
                    for candle in candles
                ])

                # Classify regime
                context = orchestrator.market_context_engine.analyze(
                    ohlcv=ohlcv_df
                )

                results.append({
                    "pair": pair,
                    "success": True,
                    "regime": context.regime,
                    "confidence": context.regime_confidence,
                    "volatility_regime": context.volatility_regime,
                    "volatility_level": context.volatility_level,
                    "sentiment_direction": context.sentiment_direction,
                    "data_quality": context.data_quality,
                    "candles_analyzed": len(candles),
                    "timestamp": datetime.utcnow().isoformat()
                })

                logger.info(f"Regime classified for {pair}: {context.regime} (confidence: {context.regime_confidence:.2f})")

            except requests.RequestException as e:
                logger.error(f"Network error fetching {pair}: {e}")
                results.append({
                    "pair": pair,
                    "success": False,
                    "error": f"Network error: {str(e)}"
                })
            except Exception as e:
                logger.error(f"Error processing {pair}: {e}")
                results.append({
                    "pair": pair,
                    "success": False,
                    "error": str(e)
                })

        # Summary
        successful = sum(1 for r in results if r.get("success"))
        total = len(results)

        return {
            "success": successful > 0,
            "regimes": results,
            "summary": {
                "total_pairs": total,
                "successful": successful,
                "failed": total - successful
            },
            "timestamp": datetime.utcnow().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Regime refresh failed: {e}")
        raise HTTPException(status_code=500, detail=f"Refresh error: {str(e)}")


# ========================================
# Startup/Shutdown
# ========================================

@app.on_event("startup")
async def startup_event():
    """Initialize SIL on startup."""
    logger.info("Starting Strategic Intelligence Layer API...")
    get_orchestrator()  # Initialize orchestrator
    logger.info("SIL API ready")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down SIL API...")


# ========================================
# Development server
# ========================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
