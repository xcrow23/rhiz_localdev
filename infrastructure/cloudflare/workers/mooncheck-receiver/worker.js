// mooncheck-receiver — Cloudflare Worker
// Retrieved from Cloudflare 2026-02-27 (chrysalis capture)
// Purpose: Receives mooncheck transcripts and forwards to VPS at api.dreamthewilderness.com
// Created: 2026-01-10 | Last modified: 2026-01-10

var __defProp = Object.defineProperty;
var __name = (target, value) => __defProp(target, "name", { value, configurable: true });

// src/mooncheck.ts
var CORS_HEADERS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type"
};
function handleOptions() {
  return new Response(null, {
    status: 204,
    headers: CORS_HEADERS
  });
}
__name(handleOptions, "handleOptions");
function validateRequest(body) {
  if (!body.transcript || typeof body.transcript !== "string") {
    return {
      valid: false,
      error: "Missing or invalid field: transcript (required, must be string)"
    };
  }
  if (!body.topic_hint || typeof body.topic_hint !== "string") {
    return {
      valid: false,
      error: "Missing or invalid field: topic_hint (required, must be string)"
    };
  }
  if (body.transcript.trim().length === 0) {
    return {
      valid: false,
      error: "Transcript cannot be empty"
    };
  }
  if (body.topic_hint.trim().length === 0) {
    return {
      valid: false,
      error: "Topic hint cannot be empty"
    };
  }
  return { valid: true };
}
__name(validateRequest, "validateRequest");
function jsonResponse(data, status = 200) {
  return new Response(JSON.stringify(data, null, 2), {
    status,
    headers: {
      "Content-Type": "application/json",
      ...CORS_HEADERS
    }
  });
}
__name(jsonResponse, "jsonResponse");
var mooncheck_default = {
  async fetch(request, env, ctx) {
    if (request.method === "OPTIONS") {
      return handleOptions();
    }
    if (request.method !== "POST") {
      return jsonResponse(
        {
          success: false,
          message: "Method not allowed. Use POST to submit moonchecks."
        },
        405
      );
    }
    try {
      let body;
      try {
        body = await request.json();
      } catch (e) {
        return jsonResponse(
          {
            success: false,
            message: "Invalid JSON in request body",
            error: e instanceof Error ? e.message : "Unknown parsing error"
          },
          400
        );
      }
      const validation = validateRequest(body);
      if (!validation.valid) {
        return jsonResponse(
          {
            success: false,
            message: validation.error || "Validation failed"
          },
          400
        );
      }
      const payload = {
        transcript: body.transcript.trim(),
        topic_hint: body.topic_hint.trim(),
        category: body.category?.trim() || "blog"
      };
      const vpsUrl = env.VPS_API_URL || "https://api.dreamthewilderness.com";
      const endpoint = `${vpsUrl}/mooncheck/ingest`;
      console.log(`[Mooncheck] Forwarding to VPS: ${endpoint}`);
      console.log(
        `[Mooncheck] Payload: topic="${payload.topic_hint}", category="${payload.category}", transcript_length=${payload.transcript.length}`
      );
      const vpsResponse = await fetch(endpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "User-Agent": "Rhiz-Cloudflare-Worker/1.0"
        },
        body: JSON.stringify(payload)
      });
      const responseData = await vpsResponse.json();
      if (vpsResponse.ok) {
        console.log(
          `[Mooncheck] Success: ID=${responseData.mooncheck_id}, timestamp=${responseData.timestamp}`
        );
      } else {
        console.error(
          `[Mooncheck] VPS error: status=${vpsResponse.status}, message=${responseData.message}`
        );
      }
      return jsonResponse(responseData, vpsResponse.status);
    } catch (error) {
      console.error("[Mooncheck] Unexpected error:", error);
      return jsonResponse(
        {
          success: false,
          message: "Internal server error",
          error: error instanceof Error ? error.message : "Unknown error"
        },
        500
      );
    }
  }
};
export {
  mooncheck_default as default
};
