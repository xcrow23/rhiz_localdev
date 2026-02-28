/**
 * Daily Health Check Worker
 * Monitors all trading platform services and logs to D1
 * Schedule: Every 4 hours
 */

export default {
  async scheduled(event, env, ctx) {
    const timestamp = new Date().toISOString();
    const hostingerVPS = '72.62.81.128';

    const services = [
      {
        name: 'sil',
        url: `http://${hostingerVPS}:8001/health`,
        description: 'Strategic Intelligence Layer',
        requiresAuth: true
      },
      {
        name: 'qdrant',
        url: `http://${hostingerVPS}:6333/collections`,
        description: 'Qdrant Vector Database',
        requiresAuth: false
      },
      {
        name: 'gateway',
        url: `http://${hostingerVPS}:8080/health`,
        description: 'FastAPI Gateway',
        requiresAuth: true
      }
    ];

    const results = [];
    let allHealthy = true;

    // Check each service
    for (const service of services) {
      const start = Date.now();

      try {
        // Verify HEALTH_CHECK_KEY is configured for authenticated services
        if (service.requiresAuth && !env.HEALTH_CHECK_KEY) {
          throw new Error('HEALTH_CHECK_KEY environment variable not configured');
        }

        // Build headers conditionally
        const headers = {};
        if (service.requiresAuth) {
          headers['X-Health-Check-Key'] = env.HEALTH_CHECK_KEY;
        }

        const response = await fetch(service.url, {
          method: 'GET',
          headers,
          signal: AbortSignal.timeout(5000)
        });

        const responseTime = Date.now() - start;
        const isHealthy = response.ok;

        if (!isHealthy) allHealthy = false;

        results.push({
          service: service.name,
          status: isHealthy ? 'healthy' : 'unhealthy',
          responseTime,
          statusCode: response.status,
          description: service.description
        });

        // Log to D1
        await env.DB.prepare(
          `INSERT INTO health_checks (timestamp, service, status, details, response_time_ms)
           VALUES (?, ?, ?, ?, ?)`
        ).bind(
          timestamp,
          service.name,
          isHealthy ? 'healthy' : 'unhealthy',
          JSON.stringify({
            statusCode: response.status,
            description: service.description
          }),
          responseTime
        ).run();

      } catch (error) {
        allHealthy = false;

        results.push({
          service: service.name,
          status: 'error',
          error: error.message,
          description: service.description
        });

        // Log error to D1
        await env.DB.prepare(
          `INSERT INTO health_checks (timestamp, service, status, details, response_time_ms)
           VALUES (?, ?, ?, ?, ?)`
        ).bind(
          timestamp,
          service.name,
          'error',
          JSON.stringify({ error: error.message }),
          null
        ).run();
      }
    }

    // Log worker execution
    await env.DB.prepare(
      `INSERT INTO worker_executions (timestamp, worker_name, execution_status, duration_ms, error_message)
       VALUES (?, ?, ?, ?, ?)`
    ).bind(
      timestamp,
      'daily-health-check',
      allHealthy ? 'success' : 'degraded',
      null,
      allHealthy ? null : 'Some services unhealthy'
    ).run();

    console.log(`[Health Check ${timestamp}] Overall: ${allHealthy ? 'HEALTHY' : 'DEGRADED'}`);
    console.log('Results:', JSON.stringify(results, null, 2));

    return new Response(JSON.stringify({
      timestamp,
      overall: allHealthy ? 'healthy' : 'degraded',
      results
    }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' }
    });
  }
};
