/**
 * Strategy Refresh Worker
 * Triggers SIL to refresh market regime classifications
 * Schedule: Daily at 12:00 UTC (6am CT)
 */

export default {
  async scheduled(event, env, ctx) {
    const timestamp = new Date().toISOString();
    const hostingerVPS = '72.62.81.128';
    const executionStart = Date.now();

    try {
      // Call SIL to refresh market regime classifications
      const silURL = `http://${hostingerVPS}:8001/refresh_regimes`;

      let result;
      let responseTime;

      try {
        const start = Date.now();
        const response = await fetch(silURL, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            pairs: ['BTC/USD', 'ETH/USD'],
            full_refresh: true
          }),
          signal: AbortSignal.timeout(30000)
        });

        responseTime = Date.now() - start;
        result = await response.json();

        console.log('[Strategy Refresh] SIL response:', result);

      } catch (silError) {
        // SIL endpoint may not exist yet - log placeholder
        console.log('[Strategy Refresh] SIL refresh endpoint not available yet');

        result = {
          success: false,
          error: 'SIL refresh_regimes endpoint not implemented yet',
          placeholder: true,
          message: 'Strategy refresh worker deployed, waiting for SIL endpoint implementation'
        };
        responseTime = null;
      }

      // Log execution to D1
      const executionTime = Date.now() - executionStart;
      await env.DB.prepare(
        `INSERT INTO worker_executions (timestamp, worker_name, execution_status, duration_ms, error_message)
         VALUES (?, ?, ?, ?, ?)`
      ).bind(
        timestamp,
        'strategy-refresh',
        result.success ? 'success' : 'pending_sil_endpoint',
        executionTime,
        result.success ? null : (result.error || 'SIL endpoint not available')
      ).run();

      // Log strategy execution if successful
      if (result.success && result.regimes) {
        for (const regime of result.regimes) {
          await env.DB.prepare(
            `INSERT INTO strategy_executions (timestamp, strategy_name, action, result, pnl_usd)
             VALUES (?, ?, ?, ?, ?)`
          ).bind(
            timestamp,
            `regime_${regime.pair.replace('/', '')}`,
            'refresh',
            JSON.stringify({
              regime: regime.regime,
              confidence: regime.confidence,
              volatility_regime: regime.volatility_regime,
              volatility_level: regime.volatility_level,
              sentiment_direction: regime.sentiment_direction,
              data_quality: regime.data_quality,
              candles_analyzed: regime.candles_analyzed
            }),
            null
          ).run();
        }

        console.log('[Strategy Refresh] Regimes logged to D1');
      } else {
        console.log('[Strategy Refresh] Placeholder execution logged');
      }

      return new Response(JSON.stringify({
        timestamp,
        status: result.success ? 'executed' : 'pending_sil_endpoint',
        result,
        responseTime
      }), {
        status: result.success ? 200 : 503,
        headers: { 'Content-Type': 'application/json' }
      });

    } catch (error) {
      const executionTime = Date.now() - executionStart;

      // Log error
      await env.DB.prepare(
        `INSERT INTO worker_executions (timestamp, worker_name, execution_status, duration_ms, error_message)
         VALUES (?, ?, ?, ?, ?)`
      ).bind(
        timestamp,
        'strategy-refresh',
        'error',
        executionTime,
        error.message
      ).run();

      console.error('[Strategy Refresh] Worker error:', error);

      return new Response(JSON.stringify({
        timestamp,
        status: 'error',
        error: error.message
      }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      });
    }
  }
};
