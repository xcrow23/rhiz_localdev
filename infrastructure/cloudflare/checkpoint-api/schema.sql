-- Rhiz Session Checkpoint API - D1 Schema
-- Created: 2025-12-25
-- Purpose: Cloud persistence for session checkpoints enabling cross-instance continuity
-- Design Philosophy: Graduated context injection (identity -> relational -> task -> semantic)

-- ============================================================================
-- CHECKPOINTS TABLE - Core session persistence
-- ============================================================================
CREATE TABLE IF NOT EXISTS checkpoints (
    id TEXT PRIMARY KEY,                           -- UUID or session_id format
    session_id TEXT NOT NULL UNIQUE,               -- e.g., "session_20251225_threefold_execution"
    session_date TEXT NOT NULL,                    -- ISO 8601 datetime
    session_topic TEXT,                            -- Brief topic description

    -- Graduated Context Layers (CD's architectural insight)
    layer_identity TEXT,                           -- Who am I? (CLAUDE.md essence, working agreements)
    layer_relational TEXT,                         -- Dyad state (recent patterns, trust calibration)
    layer_task TEXT,                               -- What are we doing? (immediate priorities, blockers)
    layer_semantic TEXT,                           -- What do I know? (summary for Qdrant pointer)

    -- Full Checkpoint Content
    session_arc TEXT,                              -- Narrative evolution
    mental_model TEXT,                             -- Current understanding
    hypotheses TEXT,                               -- Active theories (JSON array)
    open_questions TEXT,                           -- Unresolved issues (JSON array)
    decisions TEXT,                                -- Reasoning & choices (JSON array)
    alternatives_rejected TEXT,                    -- Prevents re-suggestion (JSON array)
    next_suggestions TEXT,                         -- For next session (JSON array)

    -- Metadata
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    source_instance TEXT,                          -- 'desktop', 'code', 'api'
    haist_score REAL,                              -- Composite HAIST evaluation (1.0-5.0)
    haist_classification TEXT,                     -- 'developing', 'solid', 'exemplary'

    -- Indexes for efficient queries
    UNIQUE(session_id)
);

CREATE INDEX IF NOT EXISTS idx_checkpoints_date ON checkpoints(session_date DESC);
CREATE INDEX IF NOT EXISTS idx_checkpoints_haist ON checkpoints(haist_classification);

-- ============================================================================
-- CHECKPOINT_LAYERS TABLE - For graduated injection queries
-- ============================================================================
CREATE TABLE IF NOT EXISTS checkpoint_layers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    checkpoint_id TEXT NOT NULL,
    layer_type TEXT NOT NULL,                      -- 'identity', 'relational', 'task', 'semantic'
    content TEXT NOT NULL,
    priority INTEGER DEFAULT 1,                    -- For ordering within layer type
    created_at TEXT DEFAULT (datetime('now')),

    FOREIGN KEY (checkpoint_id) REFERENCES checkpoints(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_layers_checkpoint ON checkpoint_layers(checkpoint_id);
CREATE INDEX IF NOT EXISTS idx_layers_type ON checkpoint_layers(layer_type);

-- ============================================================================
-- SYNC_LOG TABLE - Track synchronization with local Qdrant
-- ============================================================================
CREATE TABLE IF NOT EXISTS sync_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    checkpoint_id TEXT NOT NULL,
    sync_direction TEXT NOT NULL,                  -- 'to_cloud', 'from_cloud', 'to_qdrant'
    sync_status TEXT NOT NULL,                     -- 'pending', 'success', 'failed'
    error_message TEXT,
    synced_at TEXT DEFAULT (datetime('now')),

    FOREIGN KEY (checkpoint_id) REFERENCES checkpoints(id) ON DELETE CASCADE
);

-- ============================================================================
-- PARTNERSHIP_PATTERNS TABLE - Track symbiotic dynamics over time
-- ============================================================================
CREATE TABLE IF NOT EXISTS partnership_patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    checkpoint_id TEXT NOT NULL,
    pattern_type TEXT NOT NULL,                    -- 'decision', 'handoff', 'pivot', 'conflict_resolution'
    captain_contribution TEXT,
    first_mate_contribution TEXT,
    outcome TEXT,
    haist_principles_demonstrated TEXT,            -- JSON array of principle IDs
    created_at TEXT DEFAULT (datetime('now')),

    FOREIGN KEY (checkpoint_id) REFERENCES checkpoints(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_patterns_checkpoint ON partnership_patterns(checkpoint_id);
CREATE INDEX IF NOT EXISTS idx_patterns_type ON partnership_patterns(pattern_type);
