# Strategic Intelligence Layer - n8n Integration Guide

**Version:** 1.0.0
**Last Updated:** 2026-01-03
**Status:** Production-Ready

## Overview

This document describes how to integrate the Strategic Intelligence Layer (SIL) with n8n workflows for automated trading decision-making.

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐      ┌──────────────┐
│   Kraken    │─────▶│    n8n       │─────▶│  SIL API    │─────▶│  Hummingbot  │
│   Exchange  │◀─────│  Workflows   │◀─────│  (FastAPI)  │◀─────│   Gateway    │
└─────────────┘      └──────────────┘      └─────────────┘      └──────────────┘
      ▲                      ▲                     │                     │
      │                      │                     ▼                     │
      │                      │              ┌─────────────┐              │
      │                      └──────────────│   Qdrant    │              │
      │                                     │   Memory    │              │
      └─────────────────────────────────────┴─────────────┴──────────────┘
```

---

## Architecture

### Components

1. **SIL API (FastAPI):** REST endpoints for strategy selection and regime classification
2. **n8n Workflows:** Orchestration layer connecting data sources to decision engine
3. **Qdrant Memory:** Vector database for trade history and performance tracking
4. **Hummingbot Gateway:** Execution layer for placing trades on Kraken

### Data Flow

1. **Trigger:** n8n schedule node (every 1 hour for 1H strategy)
2. **Data Fetch:** n8n → Kraken REST API → OHLCV data (200+ candles)
3. **Analysis:** n8n → SIL API → Market regime classification
4. **Decision:** n8n → SIL API → Strategy selection + position sizing
5. **Execution:** n8n → Hummingbot Gateway → Place trade on Kraken
6. **Logging:** n8n → Qdrant → Store decision and outcome

---

## SIL API Endpoints

### Base URL

- **Local:** `http://localhost:8000`
- **Cloud (Hostinger VPS):** `http://sil-api:8000` (internal Docker network)
- **Public (if exposed):** `http://72.62.81.128:8000`

### Endpoints

#### 1. Health Check

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "components": {
    "market_context": "operational",
    "strategy_selector": "operational",
    "position_sizer": "operational",
    "memory": "operational",
    "learning": "disabled"
  }
}
```

#### 2. Classify Market Regime

```http
POST /regime/classify
```

**Request Body:**
```json
{
  "pair": "BTC/USD",
  "ohlcv": [
    {
      "timestamp": "2026-01-03T12:00:00Z",
      "open": 98000.0,
      "high": 98500.0,
      "low": 97800.0,
      "close": 98200.0,
      "volume": 1234.5
    },
    ...  // 200+ candles required
  ]
}
```

**Response:**
```json
{
  "pair": "BTC/USD",
  "regime": "ranging_low_vol",
  "confidence": 0.78,
  "volatility_regime": "low",
  "trend_strength": 0.15,
  "timestamp": "2026-01-03T12:00:00Z"
}
```

#### 3. Get Strategy Decision (PRIMARY ENDPOINT)

```http
POST /strategy/select
```

**Request Body:**
```json
{
  "pair": "BTC/USD",
  "ohlcv": [ ... ],  // 200+ candles
  "portfolio_balance": 52.68,
  "current_position": 0.0
}
```

**Response:**
```json
{
  "pair": "BTC/USD",
  "regime": "ranging_low_vol",
  "regime_confidence": 0.78,
  "selected_strategy": "mean_reversion",
  "action": "enter_long",
  "position_size_usd": 13.17,
  "position_size_asset": 0.000134,
  "confidence": 0.72,
  "reasoning": "BTC in ranging_low_vol regime (conf 0.78). Mean Reversion strategy selected. Price near lower Bollinger Band (oversold). Entry conditions met.",
  "risk_score": 0.25,
  "trace_fe": [
    {
      "factor": "Regime Classification",
      "evidence": "BB width 0.032 < 0.04, ATR 2.1% < 2.5%, trend_strength 0.15 < 1.0",
      "confidence": 0.78
    },
    ...
  ],
  "timestamp": "2026-01-03T12:00:00Z"
}
```

#### 4. Get Available Strategies

```http
GET /config/strategies
```

**Response:**
```json
{
  "BTC/USD": {
    "strategies": ["mean_reversion", "trend_following", "breakout_capture", "accumulation_dca", "risk_off"],
    "global_settings": {
      "max_active_strategies": 1,
      "max_daily_loss": 0.05
    }
  },
  "ETH/USD": { ... },
  "SOL/USD": { ... }
}
```

---

## n8n Workflow Design

### 1. Hourly Trading Decision Workflow

**Workflow Name:** `SIL_Hourly_Trading_Decision`
**Trigger:** Schedule (every 1 hour)

#### Nodes:

1. **Schedule Trigger**
   - Cron: `0 * * * *` (every hour)

2. **Fetch OHLCV Data**
   - HTTP Request to Kraken API
   - Endpoint: `GET https://api.kraken.com/0/public/OHLC`
   - Params:
     ```json
     {
       "pair": "XXBTZUSD",
       "interval": "60",
       "since": "{{ $now.minus({hours: 200}) }}"
     }
     ```

3. **Transform OHLCV Data**
   - Code Node (JavaScript):
     ```javascript
     const ohlcvData = $input.all()[0].json.result.XXBTZUSD;
     const transformed = ohlcvData.map(candle => ({
       timestamp: new Date(candle[0] * 1000).toISOString(),
       open: parseFloat(candle[1]),
       high: parseFloat(candle[2]),
       low: parseFloat(candle[3]),
       close: parseFloat(candle[4]),
       volume: parseFloat(candle[6])
     }));
     return { json: { ohlcv: transformed } };
     ```

4. **Get Portfolio Balance**
   - HTTP Request to Hummingbot Gateway
   - `GET /api/portfolio/balance`

5. **Request SIL Decision**
   - HTTP Request to SIL API
   - Method: POST
   - URL: `http://sil-api:8000/strategy/select`
   - Body:
     ```json
     {
       "pair": "BTC/USD",
       "ohlcv": "{{ $json.ohlcv }}",
       "portfolio_balance": "{{ $('Get Portfolio Balance').item.json.balance }}",
       "current_position": 0.0
     }
     ```

6. **Evaluate Decision**
   - IF Node:
     - **Condition:** `{{ $json.action === 'enter_long' }}`
     - **TRUE Branch:** Execute Trade
     - **FALSE Branch:** Log Wait Decision

7. **Execute Trade (TRUE branch)**
   - HTTP Request to Hummingbot Gateway
   - `POST /api/trade/market_order`
   - Body:
     ```json
     {
       "pair": "BTC/USD",
       "side": "buy",
       "amount_usd": "{{ $json.position_size_usd }}",
       "max_slippage": 0.005
     }
     ```

8. **Log Decision to Qdrant**
   - HTTP Request (or direct Qdrant write via n8n Qdrant node)
   - Store decision + outcome for learning

9. **Send Notification**
   - Slack/Email node (optional)
   - Notify Captain of trade execution

---

### 2. Regime Monitoring Workflow

**Workflow Name:** `SIL_Regime_Monitor`
**Trigger:** Schedule (every 4 hours)

#### Purpose:
Monitor regime shifts across BTC/ETH/SOL and alert when major regime changes occur.

#### Nodes:

1. **Schedule Trigger** (every 4 hours)
2. **Loop Over Assets** (BTC, ETH, SOL)
3. **Fetch OHLCV** for each asset
4. **Request Regime Classification** (`POST /regime/classify`)
5. **Compare with Previous Regime** (stored in n8n context or Qdrant)
6. **Detect Regime Shift**
   - IF: `current_regime !== previous_regime AND confidence > 0.70`
7. **Send Alert** (Slack/Email)
   - Message: "BTC regime shifted: ranging_low_vol → trending_bull (confidence: 0.82)"

---

### 3. Performance Tracking Workflow

**Workflow Name:** `SIL_Performance_Tracker`
**Trigger:** Schedule (daily at 00:00 UTC)

#### Purpose:
Aggregate daily performance metrics and store in Qdrant for learning engine calibration.

#### Nodes:

1. **Fetch All Trades from Last 24h** (from Hummingbot Gateway)
2. **Query SIL Decisions from Qdrant**
3. **Calculate Win Rate, R:R, PnL**
4. **Store Performance Snapshot** (`POST /internal/performance/snapshot`)
5. **Check Calibration Error**
   - Compare predicted win rate vs actual
   - Alert if error > 15%

---

## Deployment Steps

### Phase 1: Local Testing (Laptop)

1. **Start SIL API locally:**
   ```bash
   cd domains/trading/strategic_intelligence
   python -m uvicorn api:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Test health endpoint:**
   ```bash
   curl http://localhost:8000/health
   ```

3. **Create n8n workflow** (locally) to test `/strategy/select` endpoint

4. **Validate OHLCV data format** using Kraken fetcher output

---

### Phase 2: Cloud Deployment (Hostinger VPS)

#### Prerequisites:
- Hostinger VPS running (72.62.81.128)
- Docker and docker-compose installed
- n8n already deployed (accessible)

#### Deployment:

1. **Upload SIL files to VPS:**
   ```bash
   scp -r domains/trading/strategic_intelligence user@72.62.81.128:~/rhiz_localdev/domains/trading/
   ```

2. **Build and start SIL container:**
   ```bash
   ssh user@72.62.81.128
   cd ~/rhiz_localdev/domains/trading/strategic_intelligence
   docker-compose -f docker-compose.cloud.yaml up -d
   ```

3. **Verify SIL API is running:**
   ```bash
   curl http://localhost:8000/health
   ```

4. **Update n8n workflows:**
   - Change SIL API URL from `localhost:8000` to `sil-api:8000` (Docker network)
   - Import workflows from `domains/trading/strategic_intelligence/workflows/*.json`

5. **Test end-to-end workflow:**
   - Manually trigger `SIL_Hourly_Trading_Decision`
   - Verify decision logged in console
   - Check Qdrant data directory: `~/rhiz_localdev/domains/trading/strategic_intelligence/data/qdrant`

---

## n8n Workflow Templates

### Template Files (to be created):

1. `workflows/sil_hourly_trading.json` - Main trading loop
2. `workflows/sil_regime_monitor.json` - Regime shift detection
3. `workflows/sil_performance_tracker.json` - Daily metrics aggregation

**Location:** `domains/trading/strategic_intelligence/workflows/`

---

## Error Handling

### Common Issues:

1. **Insufficient OHLCV data:**
   - **Error:** `400 Bad Request: Insufficient data: need 200+ candles, got 150`
   - **Fix:** Increase `since` parameter in Kraken API call

2. **Qdrant connection failed:**
   - **Error:** `503 Service Unhealthy: Memory layer unavailable`
   - **Fix:** Check docker-compose logs, ensure Qdrant on-disk mode is configured

3. **Strategy selection returns "wait":**
   - **Cause:** Regime confidence <65%, data quality insufficient, or risk checks failed
   - **Action:** Check `reasoning` field in response for details

4. **Position size is 0:**
   - **Cause:** Portfolio balance too low, or risk manager rejected trade
   - **Action:** Check `risk_score` and `trace_fe` for rejection reason

---

## Monitoring

### Health Checks:

1. **SIL API Health:**
   ```bash
   curl http://sil-api:8000/health
   ```

2. **Qdrant Storage Size:**
   ```bash
   du -sh ~/rhiz_localdev/domains/trading/strategic_intelligence/data/qdrant
   ```

3. **n8n Execution History:**
   - Check n8n UI: Executions tab
   - Filter by `SIL_` prefix

### Alerts to Configure:

- **Regime shift detected** (Slack/Email)
- **Strategy selection failed** (>3 consecutive "wait" decisions)
- **Performance degradation** (win rate <40% over 7 days)
- **Qdrant storage exceeds 500MB** (cleanup needed)

---

## Security Considerations

### API Keys:

- **Kraken API:** Store in n8n credentials, restrict to IP whitelist
- **SIL API:** Currently no authentication (internal Docker network only)
- **Future:** Add JWT authentication for external access

### Network Isolation:

- SIL API exposed only on Docker bridge network `rhiz-network`
- No public port exposure unless explicitly needed

### Data Privacy:

- OHLCV data: Public (no privacy concerns)
- Trade decisions: Logged to Qdrant (no personal data)
- Portfolio balance: Sensitive - minimize logging

---

## Performance Optimization

### OHLCV Data Caching:

- Cache Kraken API responses in n8n for 1 minute
- Reduces API rate limit issues

### Batch Processing:

- Process multiple assets (BTC/ETH/SOL) in parallel using n8n split-in-batches node

### Qdrant Optimization:

- On-disk mode: <200MB RAM, suitable for 4GB VPS
- Server mode: 2GB+ RAM, enable when VPS upgraded to 8GB

---

## Troubleshooting

### Debug Mode:

Enable detailed logging in SIL API:

```bash
docker-compose -f docker-compose.cloud.yaml down
docker-compose -f docker-compose.cloud.yaml up --build
# Watch logs in real-time
docker-compose -f docker-compose.cloud.yaml logs -f sil-api
```

### Test Endpoints Manually:

```bash
# Test regime classification
curl -X POST http://localhost:8000/regime/classify \
  -H "Content-Type: application/json" \
  -d @test_data/btc_ohlcv_sample.json

# Test strategy selection
curl -X POST http://localhost:8000/strategy/select \
  -H "Content-Type: application/json" \
  -d @test_data/btc_decision_request.json
```

---

## Future Enhancements

### Phase 2.5:
- Embedding-based market similarity search
- Real-time confidence calibration
- Multi-asset portfolio optimization

### Phase 3:
- WebSocket streaming for real-time decisions
- GraphQL API for complex queries
- Multi-exchange support (Binance, Coinbase)

---

## Support

For issues or questions:
- Check logs: `docker-compose logs sil-api`
- Review test suite: `pytest tests/`
- Consult: `CLAUDE.md` (project philosophy)
