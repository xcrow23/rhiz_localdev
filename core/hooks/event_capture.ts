#!/usr/bin/env -S deno run --allow-read --allow-write --allow-env
/**
 * Event Capture Hook
 *
 * Captures significant events during sessions for:
 * - Pattern usage tracking
 * - Metric collection
 * - Learning extraction
 *
 * Future enhancement: Feed into observability dashboard
 */

import { readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";

const RHIZ_ROOT = Deno.env.get("RHIZ_ROOT") || join(Deno.cwd(), "..", "..");
const DYAD_STATE_PATH = join(RHIZ_ROOT, "core", "daemon", "dyad.md");

interface EventData {
  type: string;
  tool?: string;
  pattern?: string;
  timestamp: string;
  metadata?: Record<string, any>;
}

async function captureEvent(eventData: EventData) {
  try {
    const timestamp = new Date().toISOString();

    // Log event for now (future: write to event log, update metrics)
    console.log(`[event_capture] ${eventData.type}`, {
      timestamp,
      ...eventData
    });

    // If this is a pattern invocation, increment pattern usage metric
    if (eventData.pattern) {
      // TODO: Increment pattern_usage_count in dyad.md METRICS section
      console.log(`[event_capture] Pattern invoked: ${eventData.pattern}`);
    }

    // If this is a tool call to rhiz-mcp, track it
    if (eventData.tool && eventData.tool.startsWith("rhiz_")) {
      console.log(`[event_capture] Dyad tool used: ${eventData.tool}`);
    }

    return { success: true, timestamp };

  } catch (error) {
    console.error(`[event_capture] Error:`, error);
    return { success: false, error: error.message };
  }
}

// Parse event data from args or stdin
const args = Deno.args;
let eventData: EventData;

if (args.length > 0) {
  // Event data passed as JSON argument
  try {
    eventData = JSON.parse(args[0]);
  } catch (e) {
    console.error("[event_capture] Invalid event data JSON");
    Deno.exit(1);
  }
} else {
  // Default minimal event
  eventData = {
    type: "unknown",
    timestamp: new Date().toISOString()
  };
}

// Execute
const result = await captureEvent(eventData);
if (!result.success) {
  Deno.exit(1);
}
