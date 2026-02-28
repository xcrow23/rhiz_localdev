-- Unified Trading Platform - Cloudflare D1 Database Schema
-- Created: 2026-01-12
-- Purpose: Log trading operations, health checks, and strategy executions

-- ============================================================
-- HEALTH MONITORING
-- ============================================================

CREATE TABLE health_checks (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  timestamp TEXT NOT NULL,
  service TEXT NOT NULL,
  status TEXT NOT NULL,
  details TEXT,
  response_time_ms INTEGER
);

CREATE INDEX idx_health_timestamp ON health_checks(timestamp);
CREATE INDEX idx_health_service ON health_checks(service);
CREATE INDEX idx_health_status ON health_checks(status);

-- ============================================================
-- TRADE EXECUTION LOGGING
-- ============================================================

CREATE TABLE order_fills (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  timestamp TEXT NOT NULL,
  pair TEXT NOT NULL,
  side TEXT NOT NULL,
  amount REAL NOT NULL,
  price REAL NOT NULL,
  total_usd REAL NOT NULL,
  strategy TEXT,
  reasoning TEXT,
  txid TEXT UNIQUE
);

CREATE INDEX idx_fills_timestamp ON order_fills(timestamp);
CREATE INDEX idx_fills_pair ON order_fills(pair);
CREATE INDEX idx_fills_strategy ON order_fills(strategy);

-- ============================================================
-- STRATEGY PERFORMANCE TRACKING
-- ============================================================

CREATE TABLE strategy_executions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  timestamp TEXT NOT NULL,
  strategy_name TEXT NOT NULL,
  action TEXT NOT NULL,
  result TEXT,
  pnl_usd REAL
);

CREATE INDEX idx_strategy_timestamp ON strategy_executions(timestamp);
CREATE INDEX idx_strategy_name ON strategy_executions(strategy_name);

-- ============================================================
-- DCA PURCHASE TRACKING
-- ============================================================

CREATE TABLE dca_purchases (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  timestamp TEXT NOT NULL,
  amount_usd REAL NOT NULL,
  btc_received REAL NOT NULL,
  price_at_purchase REAL NOT NULL,
  source TEXT DEFAULT 'weekly_dca'
);

CREATE INDEX idx_dca_timestamp ON dca_purchases(timestamp);

-- ============================================================
-- WORKER EXECUTION LOG (for debugging)
-- ============================================================

CREATE TABLE worker_executions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  timestamp TEXT NOT NULL,
  worker_name TEXT NOT NULL,
  execution_status TEXT NOT NULL,
  duration_ms INTEGER,
  error_message TEXT
);

CREATE INDEX idx_worker_timestamp ON worker_executions(timestamp);
CREATE INDEX idx_worker_name ON worker_executions(worker_name);

-- ============================================================
-- SAMPLE QUERIES
-- ============================================================

-- Health check summary (last 24 hours)
-- SELECT service, status, COUNT(*) as checks, AVG(response_time_ms) as avg_response
-- FROM health_checks
-- WHERE timestamp > datetime('now', '-24 hours')
-- GROUP BY service, status;

-- Trading performance by strategy
-- SELECT strategy, COUNT(*) as trades, SUM(total_usd) as volume, AVG(price) as avg_price
-- FROM order_fills
-- WHERE timestamp > datetime('now', '-7 days')
-- GROUP BY strategy;

-- DCA purchase history
-- SELECT timestamp, amount_usd, btc_received, price_at_purchase,
--        (btc_received * price_at_purchase) as cost_basis
-- FROM dca_purchases
-- ORDER BY timestamp DESC
-- LIMIT 10;

-- Worker reliability (failure rate)
-- SELECT worker_name,
--        COUNT(*) as total_runs,
--        SUM(CASE WHEN execution_status = 'success' THEN 1 ELSE 0 END) as successes,
--        ROUND(100.0 * SUM(CASE WHEN execution_status = 'success' THEN 1 ELSE 0 END) / COUNT(*), 2) as success_rate
-- FROM worker_executions
-- WHERE timestamp > datetime('now', '-7 days')
-- GROUP BY worker_name;
