// permaculture-ai-worker — Cloudflare Worker
// Retrieved from Cloudflare 2026-02-27 (chrysalis capture)
// Purpose: Permaculture AI assistant using Claude API directly
// Pre-dates Rhiz project. Created: 2025-10-11 | Last modified: 2025-11-19
// Endpoints: /api/ask, /api/plan, /api/diagnose, /api/grid-plan, /api/health
// Env vars required: ANTHROPIC_API_KEY
// Note: Uses claude-sonnet-4-20250514 model — update model ID on rehydration

var __defProp = Object.defineProperty;
var __name = (target, value) => __defProp(target, "name", { value, configurable: true });

// worker.js
function validateTopicRelevance(input) {
  const inScopeKeywords = [
    "permaculture","regenerative","sustainable","homestead","homesteading",
    "plant","garden","garden","grow","growing","cultivat","harvest","seed",
    "soil","compost","mulch","leaf","root","flower","fruit","vegetable","tree",
    "shrub","perennial","annual","weed","herb","ecolog","ecosystem","biodiversity",
    "wildlife","pollinator","insect","bird","native","invasive","habitat",
    "conservation","restoration","carbon","nitrogen","phosphorus","nutrient","cycle",
    "botany","botanical","species","cultivar","genus","photosynthesis","transpiration",
    "osmosis","chlorophyll","phenotype","water","irrigation","swale","pond",
    "rainwater","drainage","hydrology","soil","tilth","texture","clay","sand","silt",
    "ph","acidic","alkaline","microbe","bacteria","fungi","mycorrhiz","animal",
    "livestock","cattle","sheep","goat","chicken","bee","apiary","composting",
    "manure","pasture","grazing","rotation","design","plan","layout","zone","guild",
    "polycultur","intercrop","rotation","succession","yield","productivity","season",
    "seasonal","climate","hardiness","frost","freeze","microclimate","phenophase",
    "moon phase","lunar","medicinal","herbal","tincture","infusion","remedy","healing",
    "ethics","earthcare","peoplecare","fairshare","principle"
  ];
  const offTopicKeywords = [
    "code","program","function","variable","debug","error","homework","essay",
    "write","poem","story","fiction","homework","quiz","exam","politics","religion",
    "conspiracy","hack","crack","exploit","malware","investment","crypto","stock",
    "trading","medical","doctor","disease","prescription","drug","repair","fix",
    "mechanical","financial","tax","loan","mortgage"
  ];
  const lowerInput = input.toLowerCase();
  const hasOffTopicKeyword = offTopicKeywords.some((keyword) => lowerInput.includes(keyword));
  const hasInScopeKeyword = inScopeKeywords.some((keyword) => lowerInput.includes(keyword));
  if (hasOffTopicKeyword && !hasInScopeKeyword) {
    return { isRelevant: false, reason: "off-topic" };
  }
  if (lowerInput.length < 10 && !hasInScopeKeyword) {
    return { isRelevant: false, reason: "too-vague" };
  }
  return { isRelevant: true, reason: "in-scope" };
}
__name(validateTopicRelevance, "validateTopicRelevance");

function createRejectionMessage(validationResult) {
  const suggestions = [
    "\u2022 Garden design and planning",
    "\u2022 Companion planting and plant guilds",
    "\u2022 Soil health and regeneration",
    "\u2022 Permaculture principles and ethics",
    "\u2022 Seasonal farming and moon cycles",
    "\u2022 Ecological systems and biodiversity",
    "\u2022 Plant diagnostics and herbalism",
    "\u2022 Water management and swales",
    "\u2022 Animal integration and husbandry"
  ];
  let message = "\u{1F331} I'm specialized in permaculture and regenerative agriculture! ";
  if (validationResult.reason === "too-vague") {
    message += "Could you provide more details about your gardening or permaculture question?\n\n";
  } else {
    message += "That's outside my area of expertise, but I'd be happy to help with:\n\n";
  }
  message += suggestions.join("\n") + "\n\n";
  message += "How can I help with your permaculture or gardening needs?";
  return message;
}
__name(createRejectionMessage, "createRejectionMessage");

async function logOffTopicQuery(query, endpoint, env) {
  try {
    const logEntry = {
      timestamp: (new Date()).toISOString(),
      endpoint,
      query,
      queryLength: query.length,
      type: "off-topic-attempt"
    };
    console.log(JSON.stringify(logEntry));
  } catch (error) {
    console.error("Error logging off-topic query:", error);
  }
}
__name(logOffTopicQuery, "logOffTopicQuery");

var worker_default = {
  async fetch(request, env, ctx) {
    if (request.method === "OPTIONS") {
      return new Response(null, {
        headers: {
          "Access-Control-Allow-Origin": "*",
          "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
          "Access-Control-Allow-Headers": "Content-Type"
        }
      });
    }
    const corsHeaders = {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type"
    };
    try {
      const url = new URL(request.url);
      if (url.pathname === "/api/ask" && request.method === "POST") {
        return await handleAsk(request, env, corsHeaders);
      } else if (url.pathname === "/api/plan" && request.method === "POST") {
        return await handlePlan(request, env, corsHeaders);
      } else if (url.pathname === "/api/diagnose" && request.method === "POST") {
        return await handleDiagnose(request, env, corsHeaders);
      } else if (url.pathname === "/api/grid-plan" && request.method === "POST") {
        return await handleGridPlan(request, env, corsHeaders);
      } else if (url.pathname === "/api/health" && request.method === "GET") {
        return new Response(JSON.stringify({ status: "OK", timestamp: (new Date()).toISOString() }), {
          headers: { "Content-Type": "application/json", ...corsHeaders }
        });
      }
      return new Response("Not Found", { status: 404, headers: corsHeaders });
    } catch (error) {
      return new Response(JSON.stringify({ error: "Internal server error", details: error.message }), {
        status: 500,
        headers: { "Content-Type": "application/json", ...corsHeaders }
      });
    }
  }
};

async function handleAsk(request, env, corsHeaders) {
  try {
    const { question, context } = await request.json();
    if (!question) {
      return new Response(JSON.stringify({ error: "Question is required" }), {
        status: 400, headers: { "Content-Type": "application/json", ...corsHeaders }
      });
    }
    const validation = validateTopicRelevance(question);
    if (!validation.isRelevant) {
      await logOffTopicQuery(question, "/api/ask", env);
      return new Response(JSON.stringify({
        response: createRejectionMessage(validation), isOffTopic: true, validationReason: validation.reason
      }), { status: 200, headers: { "Content-Type": "application/json", ...corsHeaders } });
    }
    const prompt = createPermaculturePrompt(question, context);
    const response = await callClaudeAPI(prompt, env.ANTHROPIC_API_KEY);
    return new Response(JSON.stringify({
      response: response.content[0].text, usage: response.usage, isOffTopic: false
    }), { headers: { "Content-Type": "application/json", ...corsHeaders } });
  } catch (error) {
    return new Response(JSON.stringify({ error: "Failed to get AI response", details: error.message }), {
      status: 500, headers: { "Content-Type": "application/json", ...corsHeaders }
    });
  }
}
__name(handleAsk, "handleAsk");

async function handlePlan(request, env, corsHeaders) {
  try {
    const { spaceSize, soilType, goals, location } = await request.json();
    const validation = validateTopicRelevance(goals);
    if (!validation.isRelevant) {
      await logOffTopicQuery(`DESIGN: ${goals}`, "/api/plan", env);
      return new Response(JSON.stringify({
        response: createRejectionMessage(validation), isOffTopic: true, validationReason: validation.reason
      }), { status: 200, headers: { "Content-Type": "application/json", ...corsHeaders } });
    }
    const prompt = createPlanningPrompt(spaceSize, soilType, goals, location);
    const response = await callClaudeAPI(prompt, env.ANTHROPIC_API_KEY, 1200);
    return new Response(JSON.stringify({
      response: response.content[0].text, usage: response.usage, isOffTopic: false
    }), { headers: { "Content-Type": "application/json", ...corsHeaders } });
  } catch (error) {
    return new Response(JSON.stringify({ error: "Failed to generate plan", details: error.message }), {
      status: 500, headers: { "Content-Type": "application/json", ...corsHeaders }
    });
  }
}
__name(handlePlan, "handlePlan");

async function handleDiagnose(request, env, corsHeaders) {
  try {
    const { plant, problem, timeframe, location } = await request.json();
    const plantValidation = validateTopicRelevance(plant);
    const problemValidation = validateTopicRelevance(problem);
    if (!plantValidation.isRelevant || !problemValidation.isRelevant) {
      await logOffTopicQuery(`DIAGNOSE - Plant: ${plant}, Problem: ${problem}`, "/api/diagnose", env);
      return new Response(JSON.stringify({
        response: createRejectionMessage(plantValidation.isRelevant ? problemValidation : plantValidation),
        isOffTopic: true,
        validationReason: plantValidation.isRelevant ? problemValidation.reason : plantValidation.reason
      }), { status: 200, headers: { "Content-Type": "application/json", ...corsHeaders } });
    }
    const prompt = createDiagnosisPrompt(plant, problem, timeframe, location);
    const response = await callClaudeAPI(prompt, env.ANTHROPIC_API_KEY);
    return new Response(JSON.stringify({
      response: response.content[0].text, usage: response.usage, isOffTopic: false
    }), { headers: { "Content-Type": "application/json", ...corsHeaders } });
  } catch (error) {
    return new Response(JSON.stringify({ error: "Failed to diagnose issue", details: error.message }), {
      status: 500, headers: { "Content-Type": "application/json", ...corsHeaders }
    });
  }
}
__name(handleDiagnose, "handleDiagnose");

async function handleGridPlan(request, env, corsHeaders) {
  try {
    const { width, length, plants, location = "Iowa, Zone 5", zone = "5", soilType = "loam" } = await request.json();
    if (!width || !length || !plants) {
      return new Response(JSON.stringify({ error: "Width, length, and plants are required" }), {
        status: 400, headers: { "Content-Type": "application/json", ...corsHeaders }
      });
    }
    const validation = validateTopicRelevance(plants);
    if (!validation.isRelevant) {
      await logOffTopicQuery(`GRID-PLAN: ${plants}`, "/api/grid-plan", env);
      return new Response(JSON.stringify({
        response: createRejectionMessage(validation), isOffTopic: true, validationReason: validation.reason
      }), { status: 200, headers: { "Content-Type": "application/json", ...corsHeaders } });
    }
    const prompt = createGridPlanPrompt(width, length, plants, location, zone, soilType);
    const response = await callClaudeAPI(prompt, env.ANTHROPIC_API_KEY, 1500);
    return new Response(JSON.stringify({
      response: response.content[0].text, usage: response.usage, isOffTopic: false
    }), { headers: { "Content-Type": "application/json", ...corsHeaders } });
  } catch (error) {
    return new Response(JSON.stringify({ error: "Failed to generate grid plan", details: error.message }), {
      status: 500, headers: { "Content-Type": "application/json", ...corsHeaders }
    });
  }
}
__name(handleGridPlan, "handleGridPlan");

async function callClaudeAPI(prompt, apiKey, maxTokens = 1000) {
  const response = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-api-key": apiKey,
      "anthropic-version": "2023-06-01"
    },
    body: JSON.stringify({
      model: "claude-sonnet-4-20250514",  // UPDATE MODEL ID ON REHYDRATION
      max_tokens: maxTokens,
      messages: [{ role: "user", content: prompt }]
    })
  });
  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Claude API error: ${error}`);
  }
  return await response.json();
}
__name(callClaudeAPI, "callClaudeAPI");

function createPermaculturePrompt(userQuestion, context = {}) {
  const {
    location = "Iowa, Zone 5",
    soilType = "clay",
    spaceSize = "small homestead",
    currentDate = (new Date()).toLocaleDateString("en-US", { year: "numeric", month: "long", day: "numeric" }),
    season = "Current season"
  } = context;
  return `You are an expert permaculture consultant specializing in sustainable agriculture, regenerative practices, ecology, and homesteading.

SCOPE: You only answer questions related to permaculture, regenerative agriculture, ecology, botany, plant science, animal husbandry, gardening, and sustainable land management.

CONTEXT:
- Location: ${location}
- Soil type: ${soilType}
- Space: ${spaceSize}
- Current date: ${currentDate}
- Season: ${season}

USER QUESTION: ${userQuestion}

Please provide practical, location-specific advice. Format with clear sections and actionable advice.`;
}
__name(createPermaculturePrompt, "createPermaculturePrompt");

function createPlanningPrompt(spaceSize, soilType, goals, location = "Iowa, Zone 5") {
  return `You are a permaculture design consultant.

SITE DETAILS:
- Space: ${spaceSize}
- Soil: ${soilType}
- Location: ${location}
- Goals: ${goals}

Provide: zone-based design, plant guilds, ecological relationships, implementation timeline, soil management, integration opportunities.`;
}
__name(createPlanningPrompt, "createPlanningPrompt");

function createDiagnosisPrompt(plant, problem, timeframe, location = "Iowa, Zone 5") {
  return `You are a plant pathologist and permaculture expert.

PLANT: ${plant}
SYMPTOMS: ${problem}
TIMEFRAME: ${timeframe}
LOCATION: ${location}

Provide: likely causes, organic treatment steps, long-term prevention, when to expect improvement.`;
}
__name(createDiagnosisPrompt, "createDiagnosisPrompt");

function createGridPlanPrompt(width, length, plants, location = "Iowa, Zone 5", zone = "5", soilType = "loam") {
  return `You are an expert permaculture designer.

PLOT: ${width}ft x ${length}ft (${width * length} sq ft)
Location: ${location}, Zone ${zone}, Soil: ${soilType}
Plants: ${plants}

Provide: design recommendations, plant placement guide, visual layout description, care notes.`;
}
__name(createGridPlanPrompt, "createGridPlanPrompt");

export { worker_default as default };
