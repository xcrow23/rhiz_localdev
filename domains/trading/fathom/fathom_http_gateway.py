"""
Fathom HTTP API Gateway
=======================
Exposes Fathom MCP tools as HTTP endpoints for n8n integration.

Run: python3 fathom_http_gateway.py
Endpoint: http://localhost:8787

Then tunnel with: cloudflared tunnel --url http://localhost:8787
"""

import json
import asyncio
import hashlib
import hmac
import base64
import time
import urllib.request
import urllib.parse
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Optional
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Configuration
PORT = 8787
KRAKEN_API_URL = "https://api.kraken.com"
API_KEY = os.getenv("KRAKEN_API_KEY") or os.getenv("FATHOM_KRAKEN_API_KEY")
API_SECRET = os.getenv("KRAKEN_SECRET_KEY") or os.getenv("FATHOM_KRAKEN_SECRET_KEY")

# Safety limits (same as Fathom MCP)
MAX_ORDER_USD = 50.0
CAPTAIN_APPROVAL_THRESHOLD = 20.0


class KrakenClient:
    """Lightweight Kraken API client."""
    
    def __init__(self):
        self.api_key = API_KEY
        self.api_secret = API_SECRET
        
    def _sign(self, urlpath: str, data: dict) -> dict:
        """Generate Kraken API signature."""
        postdata = urllib.parse.urlencode(data)
        encoded = (str(data['nonce']) + postdata).encode()
        message = urlpath.encode() + hashlib.sha256(encoded).digest()
        signature = hmac.new(
            base64.b64decode(self.api_secret),
            message,
            hashlib.sha512
        )
        return {
            'API-Key': self.api_key,
            'API-Sign': base64.b64encode(signature.digest()).decode()
        }
    
    def _request(self, endpoint: str, data: dict = None, private: bool = False) -> dict:
        """Make API request."""
        url = f"{KRAKEN_API_URL}{endpoint}"
        
        if private:
            data = data or {}
            data['nonce'] = str(int(time.time() * 1000))
            headers = self._sign(endpoint, data)
            headers['Content-Type'] = 'application/x-www-form-urlencoded'
            req = urllib.request.Request(
                url,
                data=urllib.parse.urlencode(data).encode(),
                headers=headers,
                method='POST'
            )
        else:
            if data:
                url += '?' + urllib.parse.urlencode(data)
            req = urllib.request.Request(url)
        
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                return json.loads(response.read().decode())
        except Exception as e:
            return {"error": [str(e)]}
    
    # Public endpoints
    def get_ticker(self, pair: str) -> dict:
        return self._request(f"/0/public/Ticker", {"pair": pair})
    
    def get_ohlc(self, pair: str, interval: int = 1) -> dict:
        return self._request(f"/0/public/OHLC", {"pair": pair, "interval": interval})
    
    def get_orderbook(self, pair: str, count: int = 10) -> dict:
        return self._request(f"/0/public/Depth", {"pair": pair, "count": count})
    
    # Private endpoints
    def get_balance(self) -> dict:
        return self._request("/0/private/Balance", private=True)
    
    def get_open_orders(self) -> dict:
        return self._request("/0/private/OpenOrders", private=True)
    
    def get_trades_history(self) -> dict:
        return self._request("/0/private/TradesHistory", private=True)
    
    def add_order(self, pair: str, side: str, order_type: str, volume: float, price: float = None) -> dict:
        data = {
            "pair": pair,
            "type": side,
            "ordertype": order_type,
            "volume": str(volume)
        }
        if price and order_type == "limit":
            data["price"] = str(price)
        return self._request("/0/private/AddOrder", data, private=True)
    
    def cancel_order(self, txid: str) -> dict:
        return self._request("/0/private/CancelOrder", {"txid": txid}, private=True)


# Initialize client
client = KrakenClient()


class FathomHandler(BaseHTTPRequestHandler):
    """HTTP request handler for Fathom endpoints."""
    
    def _send_json(self, data: dict, status: int = 200):
        """Send JSON response."""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def _get_body(self) -> dict:
        """Get JSON body from request."""
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length:
            body = self.rfile.read(content_length)
            return json.loads(body.decode())
        return {}
    
    def do_OPTIONS(self):
        """Handle CORS preflight."""
        self._send_json({})
    
    def do_GET(self):
        """Handle GET requests."""
        path = self.path.split('?')[0]
        
        if path == '/health':
            self._send_json({
                "status": "healthy",
                "service": "fathom-http-gateway",
                "port": PORT,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            })
        
        elif path == '/api/balance':
            result = client.get_balance()
            if result.get("error"):
                self._send_json({"success": False, "error": result["error"]}, 400)
            else:
                balances = result.get("result", {})
                self._send_json({
                    "success": True,
                    "balances": balances,
                    "usd": float(balances.get("ZUSD", 0)),
                    "btc": float(balances.get("XXBT", 0)),
                    "eth": float(balances.get("XETH", 0))
                })
        
        elif path == '/api/open_orders':
            result = client.get_open_orders()
            if result.get("error"):
                self._send_json({"success": False, "error": result["error"]}, 400)
            else:
                orders = result.get("result", {}).get("open", {})
                self._send_json({
                    "success": True,
                    "count": len(orders),
                    "orders": [
                        {
                            "txid": txid,
                            "pair": order["descr"]["pair"],
                            "side": order["descr"]["type"],
                            "volume": order["vol"],
                            "price": order["descr"].get("price", "market")
                        }
                        for txid, order in orders.items()
                    ]
                })
        
        elif path == '/api/trades':
            result = client.get_trades_history()
            if result.get("error"):
                self._send_json({"success": False, "error": result["error"]}, 400)
            else:
                trades = result.get("result", {}).get("trades", {})
                trade_list = list(trades.items())[:10]
                self._send_json({
                    "success": True,
                    "count": len(trade_list),
                    "trades": [
                        {
                            "txid": txid,
                            "pair": trade["pair"],
                            "side": trade["type"],
                            "volume": trade["vol"],
                            "price": trade["price"],
                            "cost": trade["cost"],
                            "fee": trade["fee"],
                            "time": trade["time"]
                        }
                        for txid, trade in trade_list
                    ]
                })
        
        else:
            self._send_json({"error": "Not found", "path": path}, 404)
    
    def do_POST(self):
        """Handle POST requests."""
        path = self.path.split('?')[0]
        body = self._get_body()
        
        if path == '/api/ticker':
            pair = body.get("pair", "XXBTZUSD")
            result = client.get_ticker(pair)
            if result.get("error"):
                self._send_json({"success": False, "error": result["error"]}, 400)
            else:
                data = result["result"].get(pair, {})
                self._send_json({
                    "success": True,
                    "pair": pair,
                    "price": float(data.get("c", [0])[0]),
                    "bid": float(data.get("b", [0])[0]),
                    "ask": float(data.get("a", [0])[0]),
                    "volume_24h": float(data.get("v", [0, 0])[1]),
                    "high_24h": float(data.get("h", [0, 0])[1]),
                    "low_24h": float(data.get("l", [0, 0])[1]),
                    "timestamp": time.time()
                })
        
        elif path == '/api/ohlc':
            pair = body.get("pair", "XXBTZUSD")
            interval = body.get("interval", 1)
            result = client.get_ohlc(pair, interval)
            if result.get("error"):
                self._send_json({"success": False, "error": result["error"]}, 400)
            else:
                self._send_json({
                    "success": True,
                    "pair": pair,
                    "interval": interval,
                    "data": result.get("result", {}).get(pair, [])[-20:]  # Last 20 candles
                })
        
        elif path == '/api/orderbook':
            pair = body.get("pair", "XXBTZUSD")
            count = body.get("count", 10)
            result = client.get_orderbook(pair, count)
            if result.get("error"):
                self._send_json({"success": False, "error": result["error"]}, 400)
            else:
                data = result.get("result", {}).get(pair, {})
                self._send_json({
                    "success": True,
                    "pair": pair,
                    "bids": data.get("bids", [])[:count],
                    "asks": data.get("asks", [])[:count]
                })
        
        elif path == '/api/place_order':
            # Safety checks
            pair = body.get("pair", "XXBTZUSD")
            side = body.get("side")
            order_type = body.get("order_type", "market")
            volume = float(body.get("volume", 0))
            price = body.get("price")
            captain_approved = body.get("captain_approved", False)
            
            # Validate required fields
            if not side or not volume:
                self._send_json({
                    "success": False,
                    "error": "Missing required fields: side, volume"
                }, 400)
                return
            
            # Estimate USD value
            ticker = client.get_ticker(pair)
            if ticker.get("error"):
                self._send_json({"success": False, "error": ticker["error"]}, 400)
                return
            
            current_price = float(ticker["result"][pair]["c"][0])
            estimated_usd = current_price * volume
            
            # Check limits
            if estimated_usd > MAX_ORDER_USD:
                self._send_json({
                    "success": False,
                    "error": f"Order ${estimated_usd:.2f} exceeds limit ${MAX_ORDER_USD}",
                    "estimated_usd": estimated_usd
                }, 400)
                return
            
            if estimated_usd > CAPTAIN_APPROVAL_THRESHOLD and not captain_approved:
                self._send_json({
                    "success": False,
                    "requires_approval": True,
                    "estimated_usd": estimated_usd,
                    "message": f"Order >${CAPTAIN_APPROVAL_THRESHOLD} requires captain_approved=true"
                }, 403)
                return
            
            # Place order
            result = client.add_order(pair, side, order_type, volume, price)
            if result.get("error"):
                self._send_json({"success": False, "error": result["error"]}, 400)
            else:
                txid = result["result"]["txid"][0]
                self._send_json({
                    "success": True,
                    "txid": txid,
                    "pair": pair,
                    "side": side,
                    "volume": volume,
                    "estimated_usd": estimated_usd,
                    "message": f"Order placed: {side} {volume} {pair}"
                })
        
        elif path == '/api/cancel_order':
            txid = body.get("txid")
            if not txid:
                self._send_json({"success": False, "error": "Missing txid"}, 400)
                return
            
            result = client.cancel_order(txid)
            if result.get("error"):
                self._send_json({"success": False, "error": result["error"]}, 400)
            else:
                self._send_json({
                    "success": True,
                    "cancelled": txid,
                    "message": "Order cancelled"
                })
        
        else:
            self._send_json({"error": "Not found", "path": path}, 404)
    
    def log_message(self, format, *args):
        """Custom logging."""
        print(f"[{time.strftime('%H:%M:%S')}] {args[0]}")


def main():
    """Start the HTTP gateway."""
    if not API_KEY or not API_SECRET:
        print("ERROR: Kraken API credentials not found!")
        print("Set KRAKEN_API_KEY and KRAKEN_SECRET_KEY in .env")
        return
    
    server = HTTPServer(('0.0.0.0', PORT), FathomHandler)
    print(f"""
╔═══════════════════════════════════════════════════════════════╗
║           FATHOM HTTP GATEWAY - Ready for n8n                 ║
╠═══════════════════════════════════════════════════════════════╣
║  Local:  http://localhost:{PORT}                               ║
║  Health: http://localhost:{PORT}/health                        ║
╠═══════════════════════════════════════════════════════════════╣
║  Next: Run cloudflared tunnel --url http://localhost:{PORT}    ║
║  Then: Use tunnel URL in n8n workflows                        ║
╚═══════════════════════════════════════════════════════════════╝

Endpoints:
  GET  /health          - Health check
  GET  /api/balance     - Account balance
  GET  /api/open_orders - Open orders
  GET  /api/trades      - Trade history
  POST /api/ticker      - Get ticker {{pair}}
  POST /api/ohlc        - Get OHLC {{pair, interval}}
  POST /api/orderbook   - Get orderbook {{pair, count}}
  POST /api/place_order - Place order {{pair, side, volume, order_type}}
  POST /api/cancel_order- Cancel order {{txid}}

Safety Limits:
  MAX_ORDER_USD: ${MAX_ORDER_USD}
  CAPTAIN_APPROVAL: ${CAPTAIN_APPROVAL_THRESHOLD}+

Press Ctrl+C to stop.
""")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()


if __name__ == "__main__":
    main()
