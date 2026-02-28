---
name: SessionClose
type: dyad-protocol
domains: [all]
requires_captain: true
requires_first_mate: true
priority: critical
version: 2.0.0
invokes_tools:
  - write_checkpoint
  - update_shared_focus
  - get_dyad_state
---

# Session Close

## Purpose

Preserve session state and ensure continuity for the next session. This pattern ensures:
- Work is properly documented
- Decisions and rationale are captured
- Next actions are clear
- The dyad can resume seamlessly

A session without proper close degrades future sessions. The close is as important as the handshake.

## Dyad Roles

**Captain**:
- Confirms accuracy of session summary
- Provides corrections or additions
- Signals satisfaction or concerns
- Approves next actions

**First Mate**:
- Proposes session summary
- Identifies key decisions made
- Documents what was learned
- Suggests next actions
- Writes checkpoint for persistence

## Workflow

### Phase 1: Session Summary Proposal (First Mate)

First Mate proposes summary in this format:

```
## Session Close Summary

**Session Date**: [date]
**Duration**: [time spent]
**Domain(s)**: [active domains]

### Session Arc
[2-3 sentence narrative of what the session accomplished]

### Key Decisions
- [Decision 1]: [Rationale]
- [Decision 2]: [Rationale]

### Work Completed
- [x] [Task 1]
- [x] [Task 2]
- [ ] [Task started but not finished]

### Learning Captured
- [What we learned that should persist]

### Alternatives Rejected
- [Option we considered but didn't pursue]: [Why]

### Next Actions
1. [Specific next step]
2. [Specific next step]

### Suggested Resume Prompt
"[Context-rich prompt for starting the next session]"

---
Captain: Please confirm or correct this summary.
```

### Phase 2: Captain Review

Captain reviews and provides:
- Corrections to any inaccuracies
- Additional context worth capturing
- Confirmation of next actions
- Any final notes

### Phase 3: Checkpoint Write (First Mate)

Upon Captain confirmation, First Mate executes:

**Tool call 1: Construct checkpoint data**

```python
checkpoint_data = {
    "session_id": f"session_{timestamp}",
    "date": current_date,
    "duration_minutes": calculate_session_duration(),
    "domains": active_domains,  # from dyad state

    "session_arc": captain_approved_summary,

    "working_memory": {
        "mental_model": current_understanding,
        "confidence": 0.85,  # SynLang TRACE confidence [0.0-1.0]
        "hypotheses": [
            {
                "text": "Hook integration may need Claude Code config",
                "confidence": 0.65
            }
        ],
        "active_context": what_is_loaded_in_context
    },

    "decisions": [
        {
            "decision": "what was decided",
            "rationale": "why we decided this",
            "traceable_to": "P#/G#/M# from telos (if applicable)"
        }
        # ... for each key decision
    ],

    "completed": [list of finished tasks],
    "in_progress": [list of unfinished work],

    "alternatives_rejected": [
        {
            "option": "what we didn't do",
            "reason": "why we didn't do it"
        }
        # ... for each significant alternative
    ],

    "learning": [insights and discoveries],
    "next_immediate": [specific next actions],

    "suggested_resume_prompt": rich_context_for_next_session,
    "captain_notes": any_captain_additions
}
```

**Tool call 2: Write checkpoint**

```python
filename = write_checkpoint(
    checkpoint_data=checkpoint_data,
    description=brief_session_descriptor  # e.g., "wave2_fixes"
)
# Returns: "session_20260101_wave2_fixes.yaml"
```

**Tool call 3: Update dyad state**

```python
# Clear completed blockers from shared focus
update_shared_focus(
    blockers=[],  # or keep any that persist
    next_action=next_immediate[0] if next_immediate else "Resume from checkpoint"
)

# Get updated state for confirmation
final_state = get_dyad_state()
```

**Confirmation output:**

```markdown
## Checkpoint Saved ✓

**File**: {filename}
**Location**: core/memory/checkpoints/{filename}
**Size**: {file_size_kb} KB

**Checkpoint Contents**:
- Session arc: ✓
- {decision_count} decisions documented
- {completed_count} tasks completed
- {learning_count} learnings captured
- {next_actions_count} next actions specified

**Dyad State Updated**:
- Shared focus next_action → "{next_immediate[0]}"
- Session properly closed

**For Next Session**: Load with `get_resume_context()`

Session closed. Ready for next session.
```

## Success Criteria

- Session summary accurately reflects what happened
- Key decisions documented with rationale
- Learning captured for future reference
- Next actions are specific and actionable
- Resume prompt enables seamless continuation
- Checkpoint written successfully

## Checkpoint Schema

```yaml
session_id: [timestamp]
date: [ISO date]
duration_minutes: [int]
domains: [list]

session_arc: |
  [Narrative of session]

working_memory:
  mental_model: [Current understanding]
  confidence: [0.0-1.0]  # SynLang TRACE confidence score
  hypotheses:
    - text: [Hypothesis text]
      confidence: [0.0-1.0]
  active_context: [What's loaded]

decisions:
  - decision: [What was decided]
    rationale: [Why]
    traceable_to: [Telos goal if applicable]

completed:
  - [Task 1]
  - [Task 2]

in_progress:
  - [Unfinished work]

alternatives_rejected:
  - option: [What we didn't do]
    reason: [Why not]

learning:
  - [Insight 1]
  - [Insight 2]

next_immediate:
  - [Action 1]
  - [Action 2]

suggested_resume_prompt: |
  [Rich context for next session]

captain_notes: |
  [Any Captain additions]
```

## Failure Modes

**Rushed Close**: Captain needs to leave immediately
- Resolution: First Mate writes minimal checkpoint with session arc and next actions only; full summary async

**Disagreement on Summary**: Captain's recollection differs
- Resolution: Captain's version takes precedence; document discrepancy

**No Meaningful Progress**: Session didn't accomplish expected goals
- Resolution: Document honestly; capture why; don't fabricate progress

**Checkpoint Write Failure**: Technical issue
- Resolution: Output summary in conversation as backup; retry write

## Examples

### Example 1: Standard Session Close

**First Mate**:
> ## Session Close Summary
>
> **Session Date**: January 1, 2026
> **Duration**: 2.5 hours
> **Domain(s)**: development (pattern library)
>
> ### Session Arc
> We implemented the Wave 1 pattern library for the Rhiz dyadic architecture. Created five core patterns (session_handshake, session_close, context_alignment, decision_trace, disagreement_resolution) following the dyadic reframe of Fabric patterns.
>
> ### Key Decisions
> - Pattern template structure: Chose to include both roles explicitly in every pattern
> - Directory organization: Separated by category (dyad, analysis, execution, reflection)
>
> ### Work Completed
> - [x] Created pattern directory structure
> - [x] Wrote session_handshake.md
> - [x] Wrote session_close.md
> - [x] Wrote context_alignment.md
> - [x] Wrote decision_trace.md
> - [x] Wrote disagreement_resolution.md
> - [x] Wrote patterns README.md
>
> ### Learning Captured
> - Dyadic patterns need explicit role definitions to prevent ambiguity
> - Failure modes section prevents repeating mistakes
>
> ### Alternatives Rejected
> - Single monolithic pattern file: Rejected for lack of composability
>
> ### Next Actions
> 1. Test patterns in next live session
> 2. Begin Wave 2 (daemon layer implementation)
>
> ### Suggested Resume Prompt
> "Continuing Rhiz implementation. Wave 1 (pattern library) complete. Ready for Wave 2: daemon layer with system-managed dyad.md and bidirectional MCP server."
>
> ---
> Captain: Please confirm or correct this summary.

**Captain**:
> Accurate. Add to learning: "Pattern examples help more than abstract descriptions." Good session.

**First Mate**:
> Added to learning. Writing checkpoint...
>
> ## Checkpoint Saved
>
> Location: core/memory/checkpoints/2026-01-01_session_wave1.yaml
> Dyad State: Updated
> Training Log: Appended
>
> Session properly closed. Ready for next session.

### Example 2: Rushed Close

**Captain**:
> Need to go in 2 minutes. Quick close.

**First Mate**:
> Quick checkpoint:
>
> **Session Arc**: Reviewed PAI repos, created implementation plan for Rhiz dyadic architecture.
>
> **Next Actions**: Begin Wave 1 pattern implementation.
>
> **Resume Prompt**: "Plan approved. Starting Wave 1: pattern library foundation."
>
> Writing minimal checkpoint now...
>
> Checkpoint saved. Full summary available next session if needed.

### Example 3: Session With No Progress

**First Mate**:
> ## Session Close Summary
>
> **Session Date**: January 2, 2026
> **Duration**: 1 hour
> **Domain(s)**: trading
>
> ### Session Arc
> Attempted to test sandbox order placement but encountered API authentication issues. Spent session debugging but did not resolve.
>
> ### Key Decisions
> - None - blocked by technical issue
>
> ### Work Completed
> - [ ] Sandbox order test (blocked)
>
> ### Learning Captured
> - Kraken sandbox requires separate API keys from production
> - Current credentials are production-only
>
> ### Blockers Identified
> - Need to generate sandbox API credentials via Kraken dashboard
>
> ### Next Actions
> 1. Captain: Generate sandbox API keys from Kraken
> 2. Update .env with sandbox credentials
> 3. Retry sandbox order test
>
> ### Suggested Resume Prompt
> "Continuing sandbox testing. Blocker was missing sandbox credentials. Captain should have generated new keys."
>
> ---
> Captain: Please confirm or correct this summary.

**Captain**:
> Accurate. I'll get those keys before next session.

## Usage

**Captain invocation (simple):**
```
Let's do session close.
```

**Captain invocation (rushed - minimal checkpoint):**
```
Session close - need to leave now. Quick summary only.
```

**First Mate execution:**
1. Propose session summary (Phase 1)
2. Wait for Captain confirmation (Phase 2)
3. Execute tool calls:
   - Construct checkpoint data from approved summary
   - Call `write_checkpoint(checkpoint_data, description)`
   - Call `update_shared_focus(next_action=...)`
4. Confirm checkpoint saved with details

**Estimated time**: 2-4 minutes (standard), 30 seconds (rushed)

## Tool Call Summary

**Invoked by First Mate after Captain approval:**
1. `write_checkpoint(checkpoint_data, description)` - Write session checkpoint
2. `update_shared_focus(next_action=...)` - Update dyad state
3. `get_dyad_state()` - Get final state for confirmation

## Pattern Evolution

Improve this pattern based on:
- Checkpoints that don't enable smooth resumes
- Information consistently missing from summaries
- Closes that take too long
- Checkpoints with wrong structure

## Related Patterns

- `session_handshake.md` - How we start sessions
- `context_alignment.md` - Mid-session sync
- `failure_analysis.md` (planned - Wave 5) - When sessions don't go well
