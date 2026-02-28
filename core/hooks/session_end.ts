#!/usr/bin/env -S deno run --allow-read --allow-write --allow-env
/**
 * Session End Hook
 *
 * Executes when a Claude Code session ends.
 * Updates dyad state and potentially triggers checkpoint write.
 */

import { readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";

const RHIZ_ROOT = Deno.env.get("RHIZ_ROOT") || join(Deno.cwd(), "..", "..");
const DYAD_STATE_PATH = join(RHIZ_ROOT, "core", "daemon", "dyad.md");

async function updateDyadStateOnEnd() {
  try {
    // Read current dyad.md
    let content = readFileSync(DYAD_STATE_PATH, "utf-8");

    const timestamp = new Date().toISOString();

    // Update last sync timestamp
    content = content.replace(
      /Last Updated: .*/,
      `Last Updated: ${timestamp}`
    );

    // Update FIRST_MATE_STATE last_active
    content = content.replace(
      /(## FIRST_MATE_STATE[\s\S]*?last_active:\s*).*/,
      `$1${timestamp}`
    );

    // Write updated state
    writeFileSync(DYAD_STATE_PATH, content, "utf-8");

    console.log(`[session_end] Dyad state updated`);
    console.log(`  Timestamp: ${timestamp}`);

    // TODO: Integrate with session_close pattern
    // - Check if session close pattern was executed
    // - If not, prompt for quick session summary
    // - Write checkpoint if appropriate

    return { success: true, timestamp };

  } catch (error) {
    console.error(`[session_end] Error updating dyad state:`, error);
    return { success: false, error: error.message };
  }
}

// Main execution
const result = await updateDyadStateOnEnd();
if (!result.success) {
  Deno.exit(1);
}
