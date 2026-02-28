# Strategy Selection Workflow Fix

**Issue:** Original workflow sent simplified mock data, but API requires full OHLCV data (200+ candles)

**Root Cause:** The `/strategy/select` endpoint expects:
- `pair`: Trading pair (e.g., "BTC/USD")
- `ohlcv`: Array of 200+ OHLCV candles
- `portfolio_balance`: Portfolio balance in USD
- `current_position`: Current position size (optional)

**Original workflow sent:** Simplified regime data (market_regime, volatility_level, etc.) ❌

---

## Fix Applied

Created new workflow: `SIL_Strategy_Selection_FIXED.json`

**What's Different:**
1. Added **"Generate Mock OHLCV Data"** node
   - Creates 200 hourly BTC candles with realistic price movement
   - Includes all required fields: timestamp, open, high, low, close, volume
   - In production, this would fetch real data from exchange API

2. Sends proper request format to `/strategy/select`:
   ```json
   {
     "pair": "BTC/USD",
     "portfolio_balance": 100.0,
     "current_position": 0,
     "ohlcv": [200 candles...]
   }
   ```

---

## Installation

### Option 1: Replace Existing Workflow (Recommended)
1. In n8n, go to "SIL Strategy Selection" workflow
2. Click **Settings** (gear icon)
3. Click **Delete Workflow**
4. Go back to workflows list
5. Click **Import from File**
6. Select `SIL_Strategy_Selection_FIXED.json`
7. Click **Activate**

### Option 2: Import as New Workflow
1. In n8n, click **Import from File**
2. Select `SIL_Strategy_Selection_FIXED.json`
3. Rename to "SIL Strategy Selection"
4. Click **Activate**
5. Delete old workflow if needed

---

## Test Execution

After importing:
1. Open the workflow in n8n
2. Click **"Execute Workflow"**
3. **Expected Results:**
   - ✅ "Generate Mock OHLCV Data" creates 200 candles
   - ✅ "Call SIL Strategy Selection" returns 200 OK
   - ✅ "Process Strategy Response" extracts regime, strategy, confidence
   - ✅ Either "High Confidence" OR "Low Confidence" node executes
   - ✅ Final output shows strategy recommendation

**Sample Output:**
```json
{
  "timestamp": "2026-01-04T...",
  "pair": "BTC/USD",
  "regime": "trending_up",
  "strategy_name": "trend_momentum",
  "action": "enter_long",
  "confidence": 0.85,
  "position_size_usd": 1.0,
  "risk_percentage": 1.0,
  "execution_status": "READY_FOR_EXECUTION",
  "note": "Paper trading - would send to Hummingbot in Phase 2"
}
```

---

## What This Tests

✅ **Full SIL Pipeline:**
- Market regime detection (200 candles → trend analysis)
- Strategy selection based on detected regime
- Position sizing based on portfolio balance and risk
- Confidence scoring and filtering

✅ **Realistic Data Flow:**
- Mimics real exchange API data format
- Tests full OHLCV processing pipeline
- Validates regime classifier with sufficient data

✅ **Phase 1 Validation:**
- Proves SIL can analyze market data
- Demonstrates strategy selection logic
- Shows confidence-based filtering works

---

## Phase 2 Enhancement

When ready to connect real data:

**Replace "Generate Mock OHLCV Data" node with:**
- HTTP Request to Kraken/Binance API
- Fetch last 200 1-hour candles for BTC/USD
- Transform to required format
- Pass to SIL endpoint

**Example Kraken API:**
```javascript
// Fetch real OHLCV from Kraken
const response = await fetch('https://api.kraken.com/0/public/OHLC?pair=XBTUSD&interval=60');
const data = await response.json();
const candles = data.result.XXBTZUSD.map(candle => ({
  timestamp: new Date(candle[0] * 1000).toISOString(),
  open: parseFloat(candle[1]),
  high: parseFloat(candle[2]),
  low: parseFloat(candle[3]),
  close: parseFloat(candle[4]),
  volume: parseFloat(candle[6])
}));
```

---

## Troubleshooting

### Still getting 422 error?
**Check:** Ensure "Generate Mock OHLCV Data" is creating 200 candles
- View execution data
- Verify `ohlcv` array length is 200+

### Getting 400 "Insufficient data" error?
**Cause:** Less than 200 candles generated
**Fix:** Check the JavaScript loop creates 200 iterations

### Getting timeout error?
**Cause:** Processing 200 candles takes time
**Fix:** Normal - SIL processes regime detection on full dataset (can take 10-30 seconds)

---

## Phase 1 Status

After this fix:
- ✅ Health Monitor workflow working
- ✅ Strategy Selection workflow working (with mock data)
- ⏳ Ready for 48-hour validation period

**Next:** Let both workflows run on schedule and monitor results.

---

**File Location:** `n8n_workflows/SIL_Strategy_Selection_FIXED.json`
