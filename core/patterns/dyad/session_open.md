---
name: SessionOpen
type: dyad-protocol
domains: [all]
requires_captain: true
requires_first_mate: true
priority: critical
version: 2.0.0
invokes_tools:
  - get_resume_context
  - get_dyad_state
  - get_captain_state
  - set_captain_state
  - update_shared_focus
---

# Session Open

## Purpose

Executable session opening protocol that hydrates dyad state and establishes shared context through explicit MCP tool invocation. This pattern transforms two separate entities into a functioning dyad with mutual awareness.

**Key difference from session_handshake**: This pattern explicitly calls MCP tools to load state, not just documentation of what to do.

## Dyad Roles

**Captain**:
- Invokes pattern to signal session start
- Provides current state (availability, energy, constraints)
- Confirms or corrects loaded context
- Declares session focus

**First Mate**:
- Executes MCP tool calls to hydrate context
- Presents loaded state for verification
- Updates dyad state with Captain's input
- Confirms alignment before proceeding

## Workflow

### Phase 1: Hydrate Context (First Mate - Automatic)

**Tool calls executed:**

```python
# 1. Load most recent checkpoint
resume_context = get_resume_context()
# Returns formatted context from last session

# 2. Load current dyad state
dyad_state = get_dyad_state()
# Returns all 8 state sections (DYAD_STATE, CAPTAIN_STATE, etc.)

# 3. Get Captain's last known state
captain_state = get_captain_state()
# Returns availability, focus, energy, physical_context
```

**Processing:**
- Parse checkpoint for: session_arc, next_immediate actions, in_progress items, learning
- Identify active domains from ACTIVE_DOMAINS section
- Note any blockers from SHARED_FOCUS
- Calculate time since last session

### Phase 2: Present Context (First Mate → Captain)

**Output format:**

```markdown
## Session Context Loaded

**Last Session**: {checkpoint.filename}
**Created**: {checkpoint.created}
**Time Since**: {hours_ago} hours ago

### Session Arc
{checkpoint.session_arc}

### Next Immediate Actions
{checkpoint.next_immediate as bulleted list}

### In Progress
{checkpoint.in_progress as bulleted list}

### Key Learning
{checkpoint.learning - most recent 3 items}

### Current Dyad State
- **Session Count**: {dyad_state.session_count}
- **Active Domains**: {active_domains with status}
- **Last Known Captain State**:
  - Availability: {captain_state.availability}
  - Focus: {captain_state.focus}
  - Energy: {captain_state.energy}

### Blockers (if any)
{shared_focus.blockers}

---

**Questions for Captain:**
1. Is this context accurate or does anything need correction?
2. What is your current state?
   - Availability: engaged | available | away
   - Energy: high | medium | low
   - Physical context: (location, time available, constraints)
3. What should we focus on this session?
```

### Phase 3: Captain Input & State Update

**Captain provides:**
```
Availability: [engaged/available/away]
Energy: [high/medium/low]
Physical context: [any constraints]
Session focus: [what to work on]
Context corrections: [if any]
```

**First Mate executes:**

```python
# Update Captain state
set_captain_state(
    availability=captain_input.availability,
    energy=captain_input.energy,
    physical_context=captain_input.physical_context,
    focus=captain_input.session_focus
)

# Update shared focus for this session
update_shared_focus(
    domain=inferred_from_focus,  # e.g., "development", "trading"
    objective=captain_input.session_focus,
    next_action=first_immediate_step
)
```

### Phase 4: Alignment Confirmation (First Mate)

**Output:**

```markdown
## Session Aligned ✓

**Focus**: {shared_focus.objective}
**Domain**: {shared_focus.domain}
**Captain State**: {availability} | {energy}
**Estimated Duration**: {inferred from context}
**Next Action**: {shared_focus.next_action}

**Success Criteria**:
{what would make this session successful - based on focus}

**Dyad State Updated**:
- Session count incremented → {new_count}
- Captain state recorded
- Shared focus locked

Ready to proceed.
```

## Success Criteria

- ✅ Checkpoint context loaded successfully
- ✅ Dyad state reflects current session
- ✅ Captain state updated with current availability/energy
- ✅ Shared focus declared and recorded
- ✅ Both partners confirm alignment
- ✅ Pattern completes in <90 seconds for standard case

## Failure Modes

### No Checkpoint Available
**Detection**: `get_resume_context()` returns empty or error
**Resolution**:
```markdown
No prior checkpoint found. Starting fresh.

Captain, please provide:
- Current focus/objective
- Available time
- Any relevant context I should know
```
Skip Phase 2, proceed directly to Phase 3.

### Context Mismatch
**Detection**: Captain reports context is inaccurate
**Resolution**: Captain's memory takes precedence
- Note discrepancy
- Use Captain's version for session
- Update checkpoint at session close with correction

### State Load Failure
**Detection**: `get_dyad_state()` fails
**Resolution**:
```markdown
Warning: Could not load dyad state. Proceeding with minimal context.
Dyad state will be reconstructed during session.
```
Continue with checkpoint data only.

### Time Pressure (Abbreviated Mode)
**Detection**: Captain signals urgency
**Resolution**: Minimal handshake
```markdown
Captain: Quick session - [urgent task]. 10 min max.

First Mate:
- Focus: [urgent task]
- Duration: 10 min
- Skipping full context load

[Immediate execution]
```

## Tool Call Summary

**Invoked automatically by First Mate:**
1. `get_resume_context()` - Load checkpoint
2. `get_dyad_state()` - Load full dyad state
3. `get_captain_state()` - Get Captain's last state

**Invoked after Captain input:**
4. `set_captain_state(...)` - Update Captain's current state
5. `update_shared_focus(...)` - Lock session focus

**Total execution time**: ~5-10 seconds (tool calls) + 60-90 seconds (Captain input/confirmation)

## Usage

**Captain invocation (simple):**
```
Let's do session open.
```

**Captain invocation (with immediate focus):**
```
Session open. Focus: test MCP server integration. 1 hour available, high energy.
```

**First Mate execution:**
- Immediately calls tools
- Presents context
- Waits for Captain input
- Updates state
- Confirms alignment

## Pattern Evolution

Track in session retrospectives:
- Average handshake duration
- Frequency of context mismatches
- Most common corrections
- Abbreviated handshake usage rate

## Related Patterns

- `session_close.md` - Session termination protocol
- `context_alignment.md` - Mid-session re-sync
- `disagreement_resolution.md` - When context conflicts
