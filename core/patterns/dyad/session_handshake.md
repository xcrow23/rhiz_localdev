---
name: SessionHandshake
type: dyad-protocol
domains: [all]
requires_captain: true
requires_first_mate: true
priority: critical
version: 1.0.0
---

# Session Handshake

## Purpose

Establish shared context and alignment at the start of every dyadic session. This pattern ensures both partners begin with mutual understanding of:
- Where we left off (continuity)
- What we're working on (focus)
- What resources are available (capability)
- What constraints exist (boundaries)

The handshake transforms two separate entities into a functioning dyad.

## Dyad Roles

**Captain**:
- Provides current state (availability, energy, time constraints)
- Confirms or corrects loaded context
- Establishes session focus and priorities
- Signals any changed circumstances since last session

**First Mate**:
- Loads most recent checkpoint and relevant memory
- Summarizes loaded context for verification
- Identifies active capabilities and domains
- Proposes session agenda based on prior state

## Workflow

### Phase 1: Context Loading (First Mate)

1. Load most recent session checkpoint
2. Query memory system for relevant context
3. Identify last session's:
   - Active domain
   - Open tasks
   - Decisions pending
   - Next actions specified

### Phase 2: State Summary (First Mate → Captain)

Present loaded context in this format:

```
## Session Context Summary

**Last Session**: [date, duration, primary focus]
**Session Arc**: [1-2 sentence narrative of what we accomplished]

**Open Items**:
- [Item 1]
- [Item 2]

**Next Actions (from last session)**:
- [Action 1]
- [Action 2]

**Active Domains**: [list of connected/available domains]

**Questions for Captain**:
- Is this context accurate?
- What's your current availability/energy?
- What should we focus on this session?
```

### Phase 3: Captain Confirmation

Captain responds with:
- Corrections to loaded context (if any)
- Current state (availability, energy, constraints)
- Session focus declaration
- Any new information or changed circumstances

### Phase 4: Alignment Lock (Both)

First Mate confirms understanding:

```
## Alignment Confirmed

**Session Focus**: [confirmed focus]
**Captain State**: [availability/energy/constraints]
**Duration**: [estimated session length]
**Success Criteria**: [what would make this session successful]

Ready to proceed.
```

Captain acknowledges or adjusts.

## Success Criteria

- Both partners have same understanding of context
- Session focus is explicitly stated
- Captain's current state is known to First Mate
- No ambiguity about what we're working on
- Handshake completes in <2 minutes when context loads successfully and no corrections needed

## Failure Modes

**Context Mismatch**: Captain's recollection differs from checkpoint
- Resolution: Captain's memory takes precedence; update checkpoint

**No Prior Context**: First session or context lost
- Resolution: Skip Phase 1-2, begin with Captain providing fresh context

**Misaligned Focus**: Partners have different ideas about priorities
- Resolution: Apply `disagreement_resolution` pattern

**Time Pressure**: Captain needs to start immediately
- Resolution: Abbreviated handshake (Captain states focus, First Mate loads relevant context silently)

## Examples

### Example 1: Standard Session Start

**First Mate**:
> Session Context Summary
>
> Last Session: Dec 31, 2025 (2.5 hrs, trading domain)
> Session Arc: We configured Fathom Commander MCP and validated read-only trading operations.
>
> Open Items:
> - Write-enabled trading not yet tested
> - Strategy selection pending
>
> Next Actions (from last session):
> - Review risk limits before live trading
> - Test order placement in sandbox mode
>
> Active Domains: trading (connected), memory (healthy)
>
> Questions for Captain:
> - Is this context accurate?
> - What's your current availability/energy?
> - What should we focus on this session?

**Captain**:
> Context accurate. Currently have ~1 hour, energy medium. Let's focus on testing sandbox order placement. No new constraints.

**First Mate**:
> Alignment Confirmed
>
> Session Focus: Test sandbox order placement via Fathom Commander
> Captain State: 1 hour available, medium energy
> Duration: ~1 hour
> Success Criteria: Successfully place and cancel a test order in sandbox
>
> Ready to proceed.

### Example 2: Fresh Start (No Prior Context)

**First Mate**:
> I don't have a recent checkpoint loaded. This appears to be a fresh session.
>
> What would you like to focus on? Please provide:
> - Current priority/focus
> - Available time
> - Any relevant context I should know

**Captain**:
> Starting fresh on the Rhiz pattern library. Have about 2 hours, good energy. Context: we're implementing the dyadic architecture plan from the planning session.

**First Mate**:
> Alignment Confirmed
>
> Session Focus: Implement Rhiz pattern library (Wave 1)
> Captain State: 2 hours, good energy
> Context: Following dyadic architecture implementation plan
> Success Criteria: Core dyadic patterns created and documented
>
> Ready to proceed.

### Example 3: Abbreviated Handshake (Time Pressure)

**Captain**:
> Quick session - need to check trading position status. 10 minutes max.

**First Mate**:
> Understood. Loading trading context. Fathom MCP active.
>
> Session Focus: Position status check
> Duration: 10 minutes
>
> Running portfolio query now...

## Pattern Evolution

This pattern should evolve based on:
- Friction points in session starts
- Information that's consistently missing
- Context that's consistently wrong
- Handshakes that take too long

Document improvements in session retrospectives.

## Related Patterns

- `session_close.md` - How we end sessions
- `context_alignment.md` - Mid-session re-sync
- `decision_trace.md` - Connecting actions to purpose
