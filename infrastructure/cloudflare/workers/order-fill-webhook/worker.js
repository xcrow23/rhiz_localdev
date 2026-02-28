/**
 * Order Fill Webhook Handler
 * Receives trade execution data and logs to D1
 * Triggered by: Fathom/FC HTTP POST on order fills
 */

export default {
  async fetch(request, env, ctx) {
    // Only accept POST requests
    if (request.method !== 'POST') {
      return new Response(JSON.stringify({
        error: 'Method not allowed',
        message: 'This endpoint only accepts POST requests'
      }), {
        status: 405,
        headers: {
          'Content-Type': 'application/json',
          'Allow': 'POST'
        }
      });
    }

    // Authenticate request via API key
    const apiKey = request.headers.get('X-API-Key');
    if (!apiKey || apiKey !== env.WEBHOOK_API_KEY) {
      return new Response(JSON.stringify({
        error: 'Unauthorized',
        message: 'Missing or invalid X-API-Key header'
      }), {
        status: 401,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    const timestamp = new Date().toISOString();

    try {
      // Parse incoming trade data
      const payload = await request.json();

      // Validate required fields
      const requiredFields = ['pair', 'side', 'amount', 'price', 'total_usd'];
      const missingFields = requiredFields.filter(field => !payload[field]);

      if (missingFields.length > 0) {
        return new Response(JSON.stringify({
          error: 'Invalid payload',
          message: `Missing required fields: ${missingFields.join(', ')}`,
          required: requiredFields
        }), {
          status: 400,
          headers: { 'Content-Type': 'application/json' }
        });
      }

      // Log order fill to D1
      await env.DB.prepare(
        `INSERT INTO order_fills (timestamp, pair, side, amount, price, total_usd, strategy, reasoning, txid)
         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`
      ).bind(
        payload.timestamp || timestamp,
        payload.pair,
        payload.side,
        payload.amount,
        payload.price,
        payload.total_usd,
        payload.strategy || 'manual',
        payload.reasoning || '',
        payload.txid || null
      ).run();

      console.log('[Order Fill] Trade logged:', {
        pair: payload.pair,
        side: payload.side,
        amount: payload.amount,
        total_usd: payload.total_usd
      });

      // Return success response
      return new Response(JSON.stringify({
        success: true,
        timestamp,
        trade: {
          pair: payload.pair,
          side: payload.side,
          amount: payload.amount,
          price: payload.price,
          total_usd: payload.total_usd
        }
      }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' }
      });

    } catch (error) {
      console.error('[Order Fill] Webhook error:', error);

      // Handle JSON parsing errors
      if (error instanceof SyntaxError) {
        return new Response(JSON.stringify({
          error: 'Invalid JSON',
          message: 'Request body must be valid JSON'
        }), {
          status: 400,
          headers: { 'Content-Type': 'application/json' }
        });
      }

      // Handle database errors
      return new Response(JSON.stringify({
        error: 'Internal server error',
        message: error.message,
        timestamp
      }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      });
    }
  }
};
