# Order Fill Webhook - Integration Guide

## Authentication

The webhook requires API key authentication via the `X-API-Key` header.

**API Key**: Stored as Cloudflare Worker secret `WEBHOOK_API_KEY`
**Value**: `+ed+iOmeEsUris7dTJ/FwvmF8MrzOFFYYzCageQQhLM=`

## Usage from Fathom

Add to Fathom's memory logger after successful order fills:

```python
# domains/trading/fathom/src/memory/logger.py

import httpx

WEBHOOK_URL = "https://rhiz-order-fill-webhook.dreadcrownest.workers.dev"
WEBHOOK_API_KEY = "+ed+iOmeEsUris7dTJ/FwvmF8MrzOFFYYzCageQQhLM="

async def log_order_fill(order_data):
    """Log order fill to Cloudflare D1 via webhook"""

    payload = {
        "timestamp": order_data.get("timestamp", datetime.utcnow().isoformat()),
        "pair": order_data["pair"],
        "side": order_data["side"],
        "amount": order_data["amount"],
        "price": order_data["price"],
        "total_usd": order_data["total_usd"],
        "strategy": order_data.get("strategy", "manual"),
        "reasoning": order_data.get("reasoning", ""),
        "txid": order_data.get("txid")
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            WEBHOOK_URL,
            json=payload,
            headers={
                "X-API-Key": WEBHOOK_API_KEY,
                "Content-Type": "application/json"
            },
            timeout=10.0
        )

        if response.status_code == 200:
            print(f"[Webhook] Order fill logged: {order_data['txid']}")
        else:
            print(f"[Webhook] Failed to log order: {response.status_code} - {response.text}")
```

## Testing

**Unauthorized request (no API key)**:
```bash
curl -X POST https://rhiz-order-fill-webhook.dreadcrownest.workers.dev \
  -H "Content-Type: application/json" \
  -d '{"pair":"BTC/USD","side":"buy","amount":0.001,"price":95000,"total_usd":95}'

# Response: {"error":"Unauthorized","message":"Missing or invalid X-API-Key header"}
```

**Authorized request (with API key)**:
```bash
curl -X POST https://rhiz-order-fill-webhook.dreadcrownest.workers.dev \
  -H "Content-Type: application/json" \
  -H "X-API-Key: +ed+iOmeEsUris7dTJ/FwvmF8MrzOFFYYzCageQQhLM=" \
  -d '{"pair":"BTC/USD","side":"buy","amount":0.001,"price":95000,"total_usd":95,"strategy":"test","txid":"test-123"}'

# Response: {"success":true,"timestamp":"2026-01-12T03:17:30.716Z","trade":{...}}
```

## Security Notes

- API key is stored as a Cloudflare Worker secret (not exposed in Git)
- For production use, rotate the API key periodically
- The key is also documented in this file for deployment reference
- If compromised, generate new key with: `wrangler secret put WEBHOOK_API_KEY`

## Deployment

```bash
# Set API key secret
echo "YOUR_NEW_API_KEY" | wrangler secret put WEBHOOK_API_KEY

# Deploy webhook
cd infrastructure/cloudflare/workers/order-fill-webhook
wrangler deploy
```
