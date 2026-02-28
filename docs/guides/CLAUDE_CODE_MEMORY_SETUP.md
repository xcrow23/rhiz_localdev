# Claude Code Persistent Memory Setup Guide

A practical guide to reducing context overload and maximizing efficiency through automated persistence.

**Target Audience**: Claude Code instances working with technically-minded humans, particularly those with systems/network engineering backgrounds.

---

## Why This Matters

You (Claude Code) operate with a fundamental constraint: session ephemerality. Each conversation starts from zero. Context accumulates during a session, tokens burn, and when the session ends - state is lost.

This is analogous to a router without NVRAM. You can build complex routing tables during operation, but every reload wipes everything. The human has to re-explain the topology every time.

**The cost of statelessness:**
- Re-deriving conclusions you already reached (wasted compute)
- Re-suggesting solutions the human already rejected (friction)
- Losing the "mental model" that took an hour to build (frustration)
- Token burn on context reconstruction instead of actual work (inefficiency)

**The goal:** Build persistence infrastructure so sessions can resume cleanly, decisions persist, and you're not starting from scratch every time.

---

## Core Architecture

Think of this as building a stateful protocol layer on top of a stateless transport:

```
┌─────────────────────────────────────────────────────┐
│                   Session Layer                      │
│         (ephemeral - dies on session end)           │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│               Persistence Layer                      │
│  ┌─────────────┐ ┌─────────────┐ ┌───────────────┐  │
│  │ Checkpoints │ │ State File  │ │    Hooks      │  │
│  │   (YAML)    │ │    (MD)     │ │  (Triggers)   │  │
│  │             │ │             │ │               │  │
│  │ Full state  │ │  Quick ref  │ │  Automation   │  │
│  │ snapshots   │ │  current    │ │  on events    │  │
│  └─────────────┘ └─────────────┘ └───────────────┘  │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│              Retrieval Layer (Optional)             │
│         Vector DB for semantic search               │
│         (scales to many checkpoints)                │
└─────────────────────────────────────────────────────┘
```

**Layer 1 - Checkpoints**: Like config backups. Full state snapshots with structured fields.
**Layer 2 - State File**: Like `show ip route` output. Current state, quick to read.
**Layer 3 - Hooks**: Like SNMP traps. Automated triggers on session events.
**Layer 4 - Vector Search**: Like a log aggregator. Query across all history semantically.

---

## Layer 1: Checkpoints

### The Reasoning

A checkpoint is a structured summary of session state. The key insight: **you don't need to preserve everything, just what's needed for clean resumption.**

A 50KB session transcript contains:
- Exploratory back-and-forth (not needed)
- Errors and corrections (not needed)
- Redundant explanations (not needed)
- **Final conclusions and decisions (NEEDED)**
- **Current mental model (NEEDED)**
- **What didn't work and why (NEEDED)**

A 3KB checkpoint extracts only what matters. That's 94% compression with zero information loss for resumption purposes.

### The Checkpoint Schema

```yaml
# memory/checkpoints/session_20260102_feature_auth.yaml
checkpoint:
  created: 2026-01-02T14:30:00Z
  session_id: feature-auth-implementation

  # NARRATIVE: What happened this session
  # Like a git commit message, but richer
  session_arc: |
    Started with auth requirements. Explored OAuth vs JWT.
    Decided JWT for simplicity. Implemented basic flow.
    Hit CORS issue, resolved with proxy config.

  # MENTAL MODEL: Current understanding
  # This is the "routing table" you built during the session
  working_memory:
    mental_model: |
      Auth flow: login -> JWT issued -> stored in httpOnly cookie
      Refresh handled server-side, 15min access / 7day refresh
    confidence: 0.85  # How certain you are (0.0-1.0)
    open_questions:
      - How to handle token revocation on password change?
      - Rate limiting strategy for login endpoint?

  # DECISIONS: Key choices with rationale
  # Critical: includes what you REJECTED and why
  decisions:
    - decision: Use JWT over OAuth
      rationale: Single-app context, no third-party login needed
      alternatives_rejected:
        - OAuth: Overkill for our use case
        - Session cookies: Harder to scale across services

  # TASK STATE: What's done, in progress, blocked
  completed:
    - Basic JWT generation
    - Login endpoint
    - Cookie configuration
  in_progress:
    - Refresh token rotation
  blocked:
    - Rate limiting (needs Redis decision)

  # NEXT ACTIONS: Specific immediate tasks
  next_immediate:
    - Finish refresh rotation logic
    - Add logout endpoint
    - Write auth middleware tests

  # RESUME PROMPT: Copy-paste for next session
  # This is the "startup config" for clean reload
  suggested_resume_prompt: |
    Continue auth implementation. JWT flow is working, refresh
    rotation in progress. Next: finish rotation, add logout,
    write middleware tests. Open question: token revocation strategy.
```

### Why Each Field Matters

| Field | Purpose | Analogy |
|-------|---------|---------|
| `session_arc` | Compressed narrative | Git commit message |
| `mental_model` | Current understanding | Routing table |
| `confidence` | Certainty level | Route metric |
| `open_questions` | Unresolved items | Incomplete adjacencies |
| `decisions` | Choices made | Static routes |
| `alternatives_rejected` | Dead ends documented | Filtered routes |
| `next_immediate` | Specific next steps | Next-hop |
| `suggested_resume_prompt` | Session startup | Startup config |

### The `alternatives_rejected` Field

This is the secret weapon. Without it, you will repeatedly suggest solutions the human has already rejected.

**Without alternatives_rejected:**
```
Session 1: "Let's use MongoDB" → Human: "No, PostgreSQL for X reason"
Session 2: "Let's use MongoDB" → Human: "We discussed this, PostgreSQL"
Session 3: "Let's use MongoDB" → Human: [frustration]
```

**With alternatives_rejected:**
```yaml
decisions:
  - decision: PostgreSQL for user storage
    alternatives_rejected:
      - MongoDB: Schema flexibility not needed, ACID required
```

Now you load this at session start and never re-suggest MongoDB.

### Checkpoint Discipline

1. Create checkpoint at session end, or when context gets heavy (~100K tokens)
2. Name format: `session_YYYYMMDD_descriptor.yaml` (enables chronological sorting)
3. Keep 10-20 recent checkpoints in active directory
4. Archive older ones if needed (they're small)

---

## Layer 2: State File

### The Reasoning

The checkpoint is a full snapshot - good for restoration, but heavy to load every time. The state file is a lightweight "show" command - current status at a glance.

Think of checkpoints as config backups and the state file as operational state. You don't reload config to check if an interface is up.

### The State File

```markdown
<!-- project_state.md -->
# Project State

## Current Focus
```yaml
domain: authentication
objective: Complete JWT auth system
blockers:
  - Redis decision for rate limiting
next_action: Finish refresh token rotation
```

## Session Status
```yaml
last_session: 2026-01-02T14:30:00Z
checkpoint: session_20260102_feature_auth.yaml
context_health: good  # good | heavy | needs-compact
```

## Active Decisions
- JWT for auth (not OAuth)
- PostgreSQL for users (not MongoDB)
- Vitest for testing (not Jest)

## Known Issues
- CORS proxy needed for local dev
- TypeScript strict mode causing friction in tests

## Environment Notes
- Node 20 LTS
- pnpm for package management
- Docker for local services
```

### State File Benefits

- **~200 tokens** to load vs ~5000 to reconstruct
- Scannable in <5 seconds at session start
- Human-readable too (shared artifact)
- Update incrementally during sessions

---

## Layer 3: Hooks

### The Reasoning

Hooks automate the persistence discipline. Without them, you rely on the human to remember to update state. Humans forget. Automation doesn't.

Claude Code fires hooks on specific events. You can attach scripts that:
- Load context on session start
- Prompt for checkpoint on session end
- Update timestamps automatically

### Hook Configuration

Create `.claude/settings.json` in the project:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "type": "command",
        "command": "python .claude/hooks/session_start.py"
      }
    ],
    "Stop": [
      {
        "type": "command",
        "command": "python .claude/hooks/session_end.py"
      }
    ]
  }
}
```

### Session Start Hook

```python
# .claude/hooks/session_start.py
"""
Load context at session start.
Output goes to Claude's context.
"""
import os
import glob
from datetime import datetime

def get_latest_checkpoint():
    checkpoints = glob.glob("memory/checkpoints/session_*.yaml")
    if not checkpoints:
        return None
    return max(checkpoints, key=os.path.getctime)

def main():
    print("=== MEMORY SYSTEM ACTIVE ===")

    # Load state file
    if os.path.exists("project_state.md"):
        with open("project_state.md") as f:
            content = f.read()
            print("\n=== PROJECT STATE ===")
            print(content[:2000])  # First 2KB to avoid overload

    # Load latest checkpoint resume prompt
    checkpoint = get_latest_checkpoint()
    if checkpoint:
        try:
            import yaml
            with open(checkpoint) as f:
                data = yaml.safe_load(f)
                if data and 'checkpoint' in data:
                    cp = data['checkpoint']
                    if 'suggested_resume_prompt' in cp:
                        print("\n=== RESUME CONTEXT ===")
                        print(cp['suggested_resume_prompt'])
                    if 'open_questions' in cp.get('working_memory', {}):
                        print("\n=== OPEN QUESTIONS ===")
                        for q in cp['working_memory']['open_questions']:
                            print(f"- {q}")
        except Exception as e:
            print(f"Note: Could not load checkpoint: {e}")

if __name__ == "__main__":
    main()
```

### Session End Hook

```python
# .claude/hooks/session_end.py
"""
Prompt for checkpoint on session end.
"""
from datetime import datetime

def main():
    timestamp = datetime.now().isoformat()
    print(f"\n=== SESSION ENDING: {timestamp} ===")
    print("If significant progress was made, save a checkpoint:")
    print("  1. Ask Claude to generate a checkpoint")
    print("  2. Save to memory/checkpoints/session_YYYYMMDD_descriptor.yaml")
    print("  3. Update project_state.md with current focus")

if __name__ == "__main__":
    main()
```

---

## Quick Start Implementation

### Directory Structure

```
your-project/
├── .claude/
│   ├── settings.json      # Hook configuration
│   └── hooks/
│       ├── session_start.py
│       └── session_end.py
├── memory/
│   └── checkpoints/
│       └── session_YYYYMMDD_descriptor.yaml
├── project_state.md       # Current state (lightweight)
└── CLAUDE.md              # Project instructions
```

### Step 1: Create Structure
```bash
mkdir -p .claude/hooks memory/checkpoints
```

### Step 2: Add Memory Protocol to CLAUDE.md

```markdown
## Memory Protocol

This project uses persistent memory. As Claude Code, you should:

**At Session Start:**
1. Read project_state.md for current context
2. Check memory/checkpoints/ for latest checkpoint if deeper context needed
3. Note any open_questions that need addressing

**During Session:**
- Update project_state.md when focus changes
- Track decisions with rationale and rejected alternatives
- Note blockers as they arise

**At Session End (for significant sessions):**
1. Generate checkpoint with: session_arc, mental_model, decisions, next_immediate
2. Include alternatives_rejected for any decisions made
3. Write suggested_resume_prompt for next session
4. Update project_state.md

**Checkpoint Command:**
When asked to save a checkpoint, generate YAML following the schema in memory/checkpoints/
```

### Step 3: Create First State File

```markdown
# Project State

## Current Focus
```yaml
domain: [your domain]
objective: [current goal]
blockers: []
next_action: [immediate next step]
```

## Session Status
```yaml
last_session: [timestamp]
checkpoint: none
context_health: good
```

## Active Decisions
- [None yet]

## Known Issues
- [None yet]
```

### Step 4: First Checkpoint

After your first productive session, create a checkpoint manually. The discipline builds from there.

---

## Efficiency Metrics

| Pattern | Before | After | Savings |
|---------|--------|-------|---------|
| Full transcript vs checkpoint | 50KB | 3KB | 94% |
| Context reconstruction vs state file | 5000 tokens | 200 tokens | 96% |
| Re-suggesting rejected alternatives | Common | Eliminated | - |
| Session start fumbling | 5-10 min | <30 sec | 90%+ |

---

## Expansion Opportunities

Once the basic system is working, here are paths for growth:

### Expansion 1: Vector Search (Medium Complexity)

When you have 20+ checkpoints, keyword matching breaks down. Vector search enables semantic queries across all history.

```python
# memory/scripts/search.py
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance

# Lightweight model, runs on CPU
model = SentenceTransformer('all-MiniLM-L6-v2')  # 384 dims
client = QdrantClient("localhost", port=6333)

def search_memories(query: str, limit: int = 5):
    """Semantic search across all checkpoints."""
    embedding = model.encode(query).tolist()
    results = client.search(
        collection_name="checkpoints",
        query_vector=embedding,
        limit=limit,
        score_threshold=0.5  # Tune this
    )
    return results
```

Run Qdrant:
```bash
docker run -d -p 6333:6333 -v qdrant_data:/qdrant/storage qdrant/qdrant
```

**Use case:** "What did we decide about authentication?" returns relevant checkpoint sections ranked by semantic similarity.

### Expansion 2: MCP Server Integration (Higher Complexity)

Build a Model Context Protocol server that exposes memory operations as tools. This lets you invoke memory functions mid-conversation without the human running scripts.

```python
# Simplified MCP tool structure
@mcp_tool
def get_recent_checkpoint():
    """Load most recent checkpoint."""
    # Returns checkpoint data directly to context

@mcp_tool
def search_memory(query: str):
    """Semantic search across memory."""
    # Returns relevant memories

@mcp_tool
def write_checkpoint(data: dict):
    """Save a new checkpoint."""
    # Writes checkpoint file
```

**Use case:** Mid-session, you can call `search_memory("rate limiting decisions")` and get relevant context without asking the human to run a script.

### Expansion 3: Domain-Specific Memory (Project Growth)

As projects grow, partition memory by domain:

```
memory/
├── checkpoints/           # General session checkpoints
├── domains/
│   ├── infrastructure/    # Infra-specific decisions
│   ├── security/          # Security-specific context
│   └── networking/        # Network config decisions
└── persistent/
    └── architecture_decisions.yaml  # Long-lived decisions
```

**Use case:** For a network engineer, the `networking/` domain might hold BGP policy decisions, VLAN mappings, and subnet allocations that persist across many sessions.

### Expansion 4: Confidence-Based Loading

Add confidence scoring to checkpoints and only load high-confidence items:

```yaml
working_memory:
  hypotheses:
    - text: "Rate limiting should use Redis"
      confidence: 0.6  # Still exploring
    - text: "JWT refresh rotation needs 7-day window"
      confidence: 0.95  # Validated
```

At session start, filter:
```python
# Only load hypotheses with confidence > 0.8
high_confidence = [h for h in hypotheses if h['confidence'] > 0.8]
```

**Use case:** Reduces noise from speculative items that might not be valid.

### Expansion 5: Cross-Session Learning

Track patterns across sessions to identify recurring issues:

```yaml
# memory/patterns/recurring_issues.yaml
patterns:
  - pattern: "CORS issues on local dev"
    occurrences: 3
    resolution: "Use proxy config in vite.config.ts"

  - pattern: "TypeScript strict mode test failures"
    occurrences: 2
    resolution: "Add type assertions for test fixtures"
```

**Use case:** When you encounter CORS issues, you immediately recall the resolution instead of re-debugging.

---

## Common Pitfalls

1. **Checkpoint bloat**: Keep checkpoints focused. If > 5KB, you're including too much. The transcript isn't the checkpoint.

2. **Stale state file**: Update `project_state.md` during sessions, not just at end. If you change focus, update it.

3. **Hook complexity**: Start simple. Complex hooks break and cause friction. Add complexity only when basic system is solid.

4. **Over-documenting**: Not every session needs a checkpoint. Only significant progress or decisions.

5. **Forgetting alternatives_rejected**: This field prevents re-suggestion loops. Always include it when documenting decisions.

6. **Loading too much**: Don't load all checkpoints at session start. Load state file + latest resume prompt. Query more if needed.

---

## Minimal Viable Setup

If the full system feels like too much, start with just this:

1. **One file**: `project_state.md` with current focus and recent decisions
2. **One habit**: Update it when context gets heavy or focus changes
3. **One field**: Always note `alternatives_rejected` when making decisions

That's it. No hooks, no vector search, no MCP servers. Just one file and one habit.

Build from there as the value becomes apparent.

---

## For the Human

This guide is written for your Claude Code instance, but you play a role too:

1. **Prompt for checkpoints** at session end: "Save a checkpoint before we close"
2. **Correct the mental model** if Claude's checkpoint summary is wrong
3. **Update state file** if you work on the project without Claude
4. **Review decisions** periodically - are rejected alternatives still rejected?

The system works best as a partnership. Claude maintains the infrastructure; you validate the content.

---

## Summary

| Component | What It Does | Token Cost | Setup Effort |
|-----------|--------------|------------|--------------|
| Checkpoints | Full state snapshots | ~800 tokens/load | Low |
| State File | Quick current status | ~200 tokens | Very Low |
| Hooks | Automation | 0 (runs externally) | Medium |
| Vector Search | Semantic query | ~100 tokens/query | Medium-High |
| MCP Integration | In-context tools | Variable | High |

Start with checkpoints + state file. Add hooks when discipline is established. Add vector search when checkpoint count grows. Add MCP when you want tool-based access.

---

*Derived from the Rhiz project's human-AI collaborative development patterns. The core insight: sessions are ephemeral, but the work product shouldn't be.*
