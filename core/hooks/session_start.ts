#!/usr/bin/env -S deno run --allow-read --allow-write --allow-env
/**
 * Session Start Hook
 *
 * Executes when a Claude Code session starts.
 * Updates dyad state with session initialization.
 */

import { readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";

const RHIZ_ROOT = Deno.env.get("RHIZ_ROOT") || join(Deno.cwd(), "..", "..");
const DYAD_STATE_PATH = join(RHIZ_ROOT, "core", "daemon", "dyad.md");

interface DyadState {
  session_count: number;
  last_sync: string;
  first_mate_session_id: string;
}

async function updateDyadState() {
  try {
    // Read current dyad.md
    let content = readFileSync(DYAD_STATE_PATH, "utf-8");

    // Generate session ID
    const sessionId = `session_${Date.now()}`;
    const timestamp = new Date().toISOString();

    // Update last sync timestamp
    content = content.replace(
      /Last Updated: .*/,
      `Last Updated: ${timestamp}`
    );

    // Update DYAD_STATE section
    content = content.replace(
      /(session_count:\s*)(\d+)/,
      (match, prefix, count) => `${prefix}${parseInt(count) + 1}`
    );

    content = content.replace(
      /(last_sync:\s*).*/,
      `$1${timestamp}`
    );

    // Update FIRST_MATE_STATE section
    content = content.replace(
      /(session_id:\s*).*/,
      `$1${sessionId}`
    );

    content = content.replace(
      /(## FIRST_MATE_STATE[\s\S]*?last_active:\s*).*/,
      `$1${timestamp}`
    );

    // Write updated state
    writeFileSync(DYAD_STATE_PATH, content, "utf-8");

    console.log(`[session_start] Dyad state updated`);
    console.log(`  Session ID: ${sessionId}`);
    console.log(`  Timestamp: ${timestamp}`);

    return { success: true, sessionId, timestamp };

  } catch (error) {
    console.error(`[session_start] Error updating dyad state:`, error);
    return { success: false, error: error.message };
  }
}

// Main execution
const result = await updateDyadState();
if (!result.success) {
  Deno.exit(1);
}
