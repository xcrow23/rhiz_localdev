/**
 * Weekly Alternating DCA Worker
 * Executes $15 DCA purchase every Monday 10pm UTC
 * Schedule: Monday at 22:00 UTC (4pm CT)
 *
 * Asset Rotation Strategy:
 * - Odd weeks (1, 3, 5...): BTC/USD ($15)
 * - Even weeks (2, 4, 6...): ETH/USD ($15)
 *
 * This provides 2-week accumulation cycles per asset while
 * maintaining weekly DCA discipline aligned with trading strategy docs.
 */

export default {
  async scheduled(event, env, ctx) {
    const timestamp = new Date().toISOString();
    const DCA_AMOUNT_USD = 15;

    // Determine which asset to buy based on ISO week number
    // Week 1 of year = odd, Week 2 = even, etc.
    const now = new Date();
    const weekNumber = getISOWeekNumber(now);
    const isOddWeek = weekNumber % 2 === 1;

    // Odd weeks: BTC, Even weeks: ETH
    const PAIR = isOddWeek ? 'BTC/USD' : 'ETH/USD';
    const ASSET = isOddWeek ? 'BTC' : 'ETH';

    console.log(`[DCA] Week ${weekNumber} (${isOddWeek ? 'odd' : 'even'}): Purchasing $${DCA_AMOUNT_USD} ${ASSET}`);

    // Log worker execution start
    const executionStart = Date.now();

    try {
      // TODO: Replace with actual FC HTTP endpoint once deployed
      // Expected endpoint: http://72.62.81.128:8767/trade/execute
      // For now, we'll log a placeholder execution

      const fcURL = 'http://72.62.81.128:8767/trade/execute';

      // Call FC HTTP Gateway with authentication
      let result;
      try {
        const response = await fetch(fcURL, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${env.FC_HTTP_API_KEY}`
          },
          body: JSON.stringify({
            action: 'buy',
            symbol: PAIR,
            amount_usd: DCA_AMOUNT_USD,
            reason: `Weekly DCA - ${ASSET} (Week ${weekNumber})`,
            strategy: 'alternating_dca'
          }),
          signal: AbortSignal.timeout(10000)
        });

        result = await response.json();

      } catch (fcError) {
        // FC gateway not available yet - log placeholder
        console.log('[DCA] FC gateway not available, logging placeholder execution');

        result = {
          success: false,
          error: 'FC HTTP gateway not deployed yet',
          placeholder: true,
          message: 'DCA worker deployed and scheduled, waiting for FC gateway integration'
        };
      }

      // Log to D1 (even if placeholder)
      if (result.success) {
        await env.DB.prepare(
          `INSERT INTO dca_purchases (timestamp, amount_usd, btc_received, price_at_purchase, source)
           VALUES (?, ?, ?, ?, ?)`
        ).bind(
          timestamp,
          DCA_AMOUNT_USD,
          result.btc_received || result.eth_received || 0,
          result.price || 0,
          `alternating_dca_${ASSET.toLowerCase()}`
        ).run();

        console.log(`[DCA] ${ASSET} purchase successful:`, result);
      } else {
        console.log(`[DCA] ${ASSET} purchase failed or placeholder:`, result);
      }

      // Log worker execution
      const executionTime = Date.now() - executionStart;
      await env.DB.prepare(
        `INSERT INTO worker_executions (timestamp, worker_name, execution_status, duration_ms, error_message)
         VALUES (?, ?, ?, ?, ?)`
      ).bind(
        timestamp,
        `alternating-dca-${ASSET.toLowerCase()}`,
        result.success ? 'success' : 'pending_fc_gateway',
        executionTime,
        result.success ? null : (result.error || 'FC gateway not available')
      ).run();

      return new Response(JSON.stringify({
        timestamp,
        status: result.success ? 'executed' : 'pending_fc_gateway',
        dca_amount: DCA_AMOUNT_USD,
        result
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
        'weekly-dca',
        'error',
        executionTime,
        error.message
      ).run();

      console.error('[DCA] Worker error:', error);

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

/**
 * Calculate ISO week number from date
 * ISO week 1 is the week with the first Thursday of the year
 * Returns: Week number (1-53)
 */
function getISOWeekNumber(date) {
  const tempDate = new Date(date.getTime());
  tempDate.setHours(0, 0, 0, 0);

  // Set to nearest Thursday: current date + 4 - current day number
  // Make Sunday's day number 7
  tempDate.setDate(tempDate.getDate() + 4 - (tempDate.getDay() || 7));

  // Get first day of year
  const yearStart = new Date(tempDate.getFullYear(), 0, 1);

  // Calculate full weeks to nearest Thursday
  const weekNo = Math.ceil((((tempDate - yearStart) / 86400000) + 1) / 7);

  return weekNo;
}
