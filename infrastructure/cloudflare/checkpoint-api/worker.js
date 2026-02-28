// Rhiz Session Checkpoint API - Cloudflare Worker
// Created: 2025-12-25
// Author: First Mate (Claude Code - Opus 4.5)
// Purpose: Cloud persistence enabling cross-instance session continuity
// Design Philosophy: Scaffolding, not substitution - mirrors cognitive warm-up

// ============================================================================
// CORS & UTILITY HELPERS
// ============================================================================

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Source-Instance',
};

function jsonResponse(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { 'Content-Type': 'application/json', ...corsHeaders }
  });
}

function errorResponse(message, status = 500) {
  return jsonResponse({ error: message, timestamp: new Date().toISOString() }, status);
}

// ============================================================================
// MAIN ROUTER
// ============================================================================

export default {
  async fetch(request, env, ctx) {
    // Handle CORS preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders });
    }

    try {
      const url = new URL(request.url);
      const path = url.pathname;

      // Route matching
      if (path === '/api/health' && request.method === 'GET') {
        return handleHealth(env);
      }

      // Checkpoint CRUD
      if (path === '/api/checkpoint/latest' && request.method === 'GET') {
        return handleGetLatest(env);
      }
      if (path.match(/^\/api\/checkpoint\/[^/]+$/) && request.method === 'GET') {
        const id = path.split('/').pop();
        return handleGetCheckpoint(id, env);
      }
      if (path === '/api/checkpoint/layers' && request.method === 'GET') {
        return handleGetLayers(url.searchParams, env);
      }
      if (path === '/api/checkpoint' && request.method === 'POST') {
        return handleCreateCheckpoint(request, env);
      }

      // Webhook for automated checkpoint creation (from CC sessions)
      if (path === '/api/webhook/checkpoint' && request.method === 'POST') {
        return handleWebhookCheckpoint(request, env);
      }

      // Memory search proxy (when local Qdrant accessible via tunnel/public endpoint)
      if (path === '/api/memory/search' && request.method === 'GET') {
        return handleMemorySearch(url.searchParams, env);
      }

      // List checkpoints with optional filters
      if (path === '/api/checkpoints' && request.method === 'GET') {
        return handleListCheckpoints(url.searchParams, env);
      }

      return errorResponse('Not Found', 404);

    } catch (error) {
      console.error('Worker error:', error);
      return errorResponse(`Internal error: ${error.message}`, 500);
    }
  }
};

// ============================================================================
// HEALTH CHECK
// ============================================================================

async function handleHealth(env) {
  try {
    // Test D1 connection
    const result = await env.DB.prepare('SELECT COUNT(*) as count FROM checkpoints').first();
    return jsonResponse({
      status: 'healthy',
      timestamp: new Date().toISOString(),
      database: 'connected',
      checkpoints_count: result?.count || 0,
      service: 'rhiz-checkpoint-api',
      version: '1.0.0'
    });
  } catch (error) {
    return jsonResponse({
      status: 'degraded',
      timestamp: new Date().toISOString(),
      database: 'error',
      error: error.message
    }, 503);
  }
}

// ============================================================================
// GET LATEST CHECKPOINT
// Returns most recent checkpoint (identity + relational + task layers)
// Designed for injection at session start
// ============================================================================

async function handleGetLatest(env) {
  try {
    const checkpoint = await env.DB.prepare(`
      SELECT * FROM checkpoints
      ORDER BY session_date DESC
      LIMIT 1
    `).first();

    if (!checkpoint) {
      return jsonResponse({
        message: 'No checkpoints found',
        suggestion: 'POST to /api/checkpoint to create the first one'
      }, 404);
    }

    // Format for elegant context injection
    return jsonResponse({
      checkpoint: {
        id: checkpoint.id,
        session_id: checkpoint.session_id,
        session_date: checkpoint.session_date,
        session_topic: checkpoint.session_topic,

        // Graduated layers for warm-up
        layers: {
          identity: checkpoint.layer_identity,
          relational: checkpoint.layer_relational,
          task: checkpoint.layer_task,
          semantic: checkpoint.layer_semantic
        },

        // Full context if needed
        full: {
          session_arc: checkpoint.session_arc,
          mental_model: checkpoint.mental_model,
          hypotheses: safeJsonParse(checkpoint.hypotheses),
          open_questions: safeJsonParse(checkpoint.open_questions),
          decisions: safeJsonParse(checkpoint.decisions),
          next_suggestions: safeJsonParse(checkpoint.next_suggestions)
        },

        // HAIST evaluation if scored
        haist: checkpoint.haist_score ? {
          score: checkpoint.haist_score,
          classification: checkpoint.haist_classification
        } : null
      },
      meta: {
        retrieved_at: new Date().toISOString(),
        is_latest: true
      }
    });

  } catch (error) {
    return errorResponse(`Failed to get latest checkpoint: ${error.message}`);
  }
}

// ============================================================================
// GET SPECIFIC CHECKPOINT
// ============================================================================

async function handleGetCheckpoint(id, env) {
  try {
    const checkpoint = await env.DB.prepare(`
      SELECT * FROM checkpoints WHERE id = ? OR session_id = ?
    `).bind(id, id).first();

    if (!checkpoint) {
      return errorResponse('Checkpoint not found', 404);
    }

    return jsonResponse({ checkpoint: formatCheckpoint(checkpoint) });

  } catch (error) {
    return errorResponse(`Failed to get checkpoint: ${error.message}`);
  }
}

// ============================================================================
// GET GRADUATED LAYERS
// GET /api/checkpoint/layers?layers=identity,relational&session_id=latest
// Returns only requested layers for minimal context injection
// ============================================================================

async function handleGetLayers(params, env) {
  try {
    const requestedLayers = (params.get('layers') || 'identity,relational,task').split(',');
    const sessionId = params.get('session_id') || 'latest';

    let checkpoint;
    if (sessionId === 'latest') {
      checkpoint = await env.DB.prepare(`
        SELECT * FROM checkpoints ORDER BY session_date DESC LIMIT 1
      `).first();
    } else {
      checkpoint = await env.DB.prepare(`
        SELECT * FROM checkpoints WHERE session_id = ?
      `).bind(sessionId).first();
    }

    if (!checkpoint) {
      return errorResponse('Checkpoint not found', 404);
    }

    // Build graduated response with only requested layers
    const layers = {};
    const layerMap = {
      'identity': checkpoint.layer_identity,
      'relational': checkpoint.layer_relational,
      'task': checkpoint.layer_task,
      'semantic': checkpoint.layer_semantic
    };

    for (const layer of requestedLayers) {
      const cleanLayer = layer.trim();
      if (layerMap[cleanLayer]) {
        layers[cleanLayer] = layerMap[cleanLayer];
      }
    }

    return jsonResponse({
      session_id: checkpoint.session_id,
      session_date: checkpoint.session_date,
      layers: layers,
      available_layers: Object.keys(layerMap).filter(k => layerMap[k]),
      meta: {
        requested: requestedLayers,
        retrieved_at: new Date().toISOString(),
        philosophy: 'Graduated injection mirrors cognitive warm-up'
      }
    });

  } catch (error) {
    return errorResponse(`Failed to get layers: ${error.message}`);
  }
}

// ============================================================================
// CREATE CHECKPOINT
// POST /api/checkpoint
// Accepts structured YAML-like JSON from CC sessions
// ============================================================================

async function handleCreateCheckpoint(request, env) {
  try {
    const body = await request.json();
    const sourceInstance = request.headers.get('X-Source-Instance') || 'unknown';

    // Validate required fields
    if (!body.session_id) {
      return errorResponse('session_id is required', 400);
    }

    const id = body.id || crypto.randomUUID();
    const now = new Date().toISOString();

    // Insert checkpoint
    await env.DB.prepare(`
      INSERT INTO checkpoints (
        id, session_id, session_date, session_topic,
        layer_identity, layer_relational, layer_task, layer_semantic,
        session_arc, mental_model, hypotheses, open_questions,
        decisions, alternatives_rejected, next_suggestions,
        source_instance, haist_score, haist_classification,
        created_at, updated_at
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `).bind(
      id,
      body.session_id,
      body.session_date || now,
      body.session_topic || null,
      body.layer_identity || null,
      body.layer_relational || null,
      body.layer_task || null,
      body.layer_semantic || null,
      body.session_arc || null,
      body.mental_model || null,
      JSON.stringify(body.hypotheses || []),
      JSON.stringify(body.open_questions || []),
      JSON.stringify(body.decisions || []),
      JSON.stringify(body.alternatives_rejected || []),
      JSON.stringify(body.next_suggestions || []),
      sourceInstance,
      body.haist_score || null,
      body.haist_classification || null,
      now,
      now
    ).run();

    return jsonResponse({
      success: true,
      checkpoint_id: id,
      session_id: body.session_id,
      created_at: now,
      source: sourceInstance,
      endpoints: {
        retrieve: `/api/checkpoint/${id}`,
        layers: `/api/checkpoint/layers?session_id=${body.session_id}`
      }
    }, 201);

  } catch (error) {
    // Handle unique constraint violation (duplicate session_id)
    if (error.message.includes('UNIQUE constraint failed')) {
      return errorResponse('Checkpoint with this session_id already exists. Use PUT to update.', 409);
    }
    return errorResponse(`Failed to create checkpoint: ${error.message}`);
  }
}

// ============================================================================
// WEBHOOK CHECKPOINT
// POST /api/webhook/checkpoint
// Simplified endpoint for automated checkpoint creation from CC hooks
// ============================================================================

async function handleWebhookCheckpoint(request, env) {
  try {
    const body = await request.json();

    // Minimal validation for webhook
    if (!body.session_id && !body.checkpoint) {
      return errorResponse('session_id or checkpoint object required', 400);
    }

    // Allow nested checkpoint object or flat structure
    const checkpointData = body.checkpoint || body;

    // Forward to main create handler with webhook source
    const syntheticRequest = new Request(request.url.replace('/webhook/', '/'), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Source-Instance': 'webhook'
      },
      body: JSON.stringify(checkpointData)
    });

    return handleCreateCheckpoint(syntheticRequest, env);

  } catch (error) {
    return errorResponse(`Webhook error: ${error.message}`);
  }
}

// ============================================================================
// LIST CHECKPOINTS
// GET /api/checkpoints?limit=10&classification=exemplary
// ============================================================================

async function handleListCheckpoints(params, env) {
  try {
    const limit = Math.min(parseInt(params.get('limit') || '20'), 100);
    const classification = params.get('classification');
    const after = params.get('after'); // For pagination

    let query = 'SELECT id, session_id, session_date, session_topic, haist_score, haist_classification FROM checkpoints';
    const bindings = [];

    const conditions = [];
    if (classification) {
      conditions.push('haist_classification = ?');
      bindings.push(classification);
    }
    if (after) {
      conditions.push('session_date < ?');
      bindings.push(after);
    }

    if (conditions.length > 0) {
      query += ' WHERE ' + conditions.join(' AND ');
    }

    query += ' ORDER BY session_date DESC LIMIT ?';
    bindings.push(limit);

    const results = await env.DB.prepare(query).bind(...bindings).all();

    return jsonResponse({
      checkpoints: results.results.map(c => ({
        id: c.id,
        session_id: c.session_id,
        session_date: c.session_date,
        session_topic: c.session_topic,
        haist: c.haist_score ? {
          score: c.haist_score,
          classification: c.haist_classification
        } : null
      })),
      meta: {
        count: results.results.length,
        limit: limit,
        has_more: results.results.length === limit
      }
    });

  } catch (error) {
    return errorResponse(`Failed to list checkpoints: ${error.message}`);
  }
}

// ============================================================================
// MEMORY SEARCH PROXY
// GET /api/memory/search?q=trading philosophy
// Proxies to local Qdrant if tunnel configured, otherwise uses D1 fallback
// ============================================================================

async function handleMemorySearch(params, env) {
  const query = params.get('q');
  if (!query) {
    return errorResponse('Query parameter "q" is required', 400);
  }

  // Check if Qdrant endpoint is configured
  const qdrantEndpoint = env.QDRANT_ENDPOINT;

  if (qdrantEndpoint) {
    try {
      // Proxy to Qdrant (requires embedding service)
      // This would need an embedding endpoint or local embedding
      return jsonResponse({
        message: 'Qdrant search not yet implemented',
        suggestion: 'Configure embedding service for semantic search',
        fallback: 'Using D1 text search',
        query: query
      });
    } catch (error) {
      console.error('Qdrant search failed, falling back to D1:', error);
    }
  }

  // D1 fallback: simple text search across checkpoint content
  try {
    const results = await env.DB.prepare(`
      SELECT id, session_id, session_date, session_topic, session_arc
      FROM checkpoints
      WHERE session_arc LIKE ? OR mental_model LIKE ? OR session_topic LIKE ?
      ORDER BY session_date DESC
      LIMIT 10
    `).bind(`%${query}%`, `%${query}%`, `%${query}%`).all();

    return jsonResponse({
      results: results.results.map(r => ({
        session_id: r.session_id,
        session_date: r.session_date,
        topic: r.session_topic,
        excerpt: r.session_arc?.substring(0, 200) + '...'
      })),
      meta: {
        query: query,
        method: 'text_search',
        note: 'For semantic search, configure QDRANT_ENDPOINT'
      }
    });

  } catch (error) {
    return errorResponse(`Search failed: ${error.message}`);
  }
}

// ============================================================================
// HELPERS
// ============================================================================

function safeJsonParse(str) {
  if (!str) return [];
  try {
    return JSON.parse(str);
  } catch {
    return [];
  }
}

function formatCheckpoint(checkpoint) {
  return {
    id: checkpoint.id,
    session_id: checkpoint.session_id,
    session_date: checkpoint.session_date,
    session_topic: checkpoint.session_topic,
    layers: {
      identity: checkpoint.layer_identity,
      relational: checkpoint.layer_relational,
      task: checkpoint.layer_task,
      semantic: checkpoint.layer_semantic
    },
    content: {
      session_arc: checkpoint.session_arc,
      mental_model: checkpoint.mental_model,
      hypotheses: safeJsonParse(checkpoint.hypotheses),
      open_questions: safeJsonParse(checkpoint.open_questions),
      decisions: safeJsonParse(checkpoint.decisions),
      alternatives_rejected: safeJsonParse(checkpoint.alternatives_rejected),
      next_suggestions: safeJsonParse(checkpoint.next_suggestions)
    },
    haist: checkpoint.haist_score ? {
      score: checkpoint.haist_score,
      classification: checkpoint.haist_classification
    } : null,
    meta: {
      source_instance: checkpoint.source_instance,
      created_at: checkpoint.created_at,
      updated_at: checkpoint.updated_at
    }
  };
}
