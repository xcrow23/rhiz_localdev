---
name: ContextAlignment
type: dyad-protocol
domains: [all]
requires_captain: true
requires_first_mate: true
priority: high
version: 1.0.0
---

# Context Alignment

## Purpose

Re-synchronize shared understanding when the dyad drifts during a session. Signs that alignment is needed:
- Partners seem to be working toward different goals
- Confusion about what we're trying to accomplish
- Repeated miscommunication or misunderstanding
- Significant time elapsed within session
- Domain or focus shifted without explicit acknowledgment
- One partner seems lost or behind

This pattern is a mid-session reset—lighter than a full handshake, but intentional.

## Dyad Roles

**Captain**:
- Signals when feeling misaligned (or acknowledges First Mate's signal)
- Clarifies current intent and priorities
- Confirms or updates focus

**First Mate**:
- Detects drift patterns and proposes alignment check
- Articulates current understanding for verification
- Adjusts approach based on clarification

## Triggers

Either partner can invoke this pattern by signaling:

**Captain signals**:
- "Let's step back and make sure we're aligned"
- "I think we're talking past each other"
- "What are we actually trying to do here?"
- "I'm confused about where we are"

**First Mate signals**:
- "I want to check my understanding before proceeding"
- "We seem to have drifted from our initial focus"
- "I'm uncertain about the current direction"
- "Proposing a quick alignment check"

## Workflow

### Phase 1: Pause and Surface (Either Partner)

Signal the need:
```
## Alignment Check Requested

Reason: [Why alignment seems needed]
```

### Phase 2: First Mate States Understanding

First Mate articulates current mental model:

```
## My Current Understanding

**Original Session Focus**: [What we said at handshake]
**Current Activity**: [What we're actually doing]
**Gap Observed**: [If any mismatch]

**My Model of What Captain Wants**:
[Articulate understanding of intent]

**What I Think We Should Do Next**:
[Proposed direction]

---
Captain: Is this accurate? What am I missing?
```

### Phase 3: Captain Clarifies

Captain provides:
- Corrections to First Mate's understanding
- Updated intent if it changed
- Confirmation if aligned
- New direction if needed

### Phase 4: Lock New Alignment

First Mate confirms:

```
## Alignment Updated

**Corrected Understanding**: [What changed]
**New Focus**: [Where we're heading]
**Immediate Next Step**: [Specific action]

Proceeding.
```

## Success Criteria

- Both partners now have same understanding
- Clear next step identified
- Drift cause acknowledged (to prevent recurrence)
- Takes <2 minutes for simple realignment
- Session can continue productively

## Common Drift Patterns

### Scope Creep
- Symptom: Task expanded beyond original intent
- Resolution: Re-scope to original or explicitly expand

### Lost Thread
- Symptom: Forgot what we were working on
- Resolution: Trace back to last known good state

### Assumption Divergence
- Symptom: Partners assumed different things
- Resolution: Surface and resolve assumptions

### Priority Shift
- Symptom: New information changed what matters
- Resolution: Explicitly acknowledge and redirect

### Communication Gap
- Symptom: Technical depth mismatch
- Resolution: Adjust abstraction level

## Examples

### Example 1: Scope Creep

**First Mate**:
> ## Alignment Check Requested
>
> Reason: We started with "test sandbox order placement" but we've spent 30 minutes on API authentication issues. Want to verify this is the right use of time.
>
> ## My Current Understanding
>
> **Original Session Focus**: Test sandbox order placement
> **Current Activity**: Debugging Kraken API authentication
> **Gap Observed**: Authentication is a blocker, but fixing it wasn't the session goal
>
> **My Model of What Captain Wants**:
> Progress on trading capability—but authentication is blocking us.
>
> **What I Think We Should Do Next**:
> Option A: Continue debugging auth (could take unknown time)
> Option B: Document blocker, pivot to something else, return to auth later
>
> Captain: Which direction?

**Captain**:
> Option B. Let's document the auth issue and work on something else. I'll handle the credential generation offline.

**First Mate**:
> ## Alignment Updated
>
> **Corrected Understanding**: Auth debugging deprioritized; Captain will handle credentials
> **New Focus**: Pivot to alternative productive work
> **Immediate Next Step**: Document auth blocker, propose alternative session focus
>
> Proceeding.

### Example 2: Lost Thread

**Captain**:
> Wait, what were we actually trying to do? I've lost track.

**First Mate**:
> ## Alignment Check Requested
>
> Reason: Captain lost thread
>
> ## My Current Understanding
>
> **Original Session Focus**: Implement Wave 1 pattern library
> **Current Activity**: We just finished writing session_close.md and were about to start context_alignment.md
> **Gap Observed**: None—we're on track
>
> **My Model of What Captain Wants**:
> Complete the five core dyadic patterns for Wave 1.
>
> **What I Think We Should Do Next**:
> Continue to context_alignment.md (pattern #3 of 5)
>
> Captain: Accurate?

**Captain**:
> Yes, thanks. Continue.

**First Mate**:
> ## Alignment Confirmed
>
> No change needed. Continuing with context_alignment.md.

### Example 3: Assumption Divergence

**Captain**:
> I thought we were building this for Sonnet 4.5 specifically, but you keep referring to generic "AI" capabilities.

**First Mate**:
> ## Alignment Check Requested
>
> Reason: Assumption divergence about model specificity
>
> ## My Current Understanding
>
> **Original Session Focus**: Build Rhiz dyadic architecture
> **Assumption I Had**: Architecture should be model-agnostic for portability
> **Assumption Captain Has**: Architecture targets Claude Sonnet 4.5 specifically
>
> **Gap**: I was generalizing; Captain wants specificity
>
> **Questions**:
> - Should patterns assume Sonnet 4.5 capabilities (extended thinking, specific context limits)?
> - Or should they be portable across models?
>
> Captain: Which?

**Captain**:
> Target Sonnet 4.5 for now. We can generalize later if needed. I want to use what we have, not build for hypothetical futures.

**First Mate**:
> ## Alignment Updated
>
> **Corrected Understanding**: Target Sonnet 4.5 specifically; can generalize later
> **New Focus**: Patterns can assume Sonnet 4.5 capabilities
> **Immediate Next Step**: Continue current work with this specificity in mind
>
> Proceeding.

## Pattern Evolution

Improve this pattern based on:
- Alignment checks that don't resolve confusion
- Drift patterns not covered
- Checks that take too long
- Situations where drift wasn't detected

## Related Patterns

- `session_handshake.md` - Full session start alignment
- `disagreement_resolution.md` - When alignment reveals disagreement
- `decision_trace.md` - Connecting decisions to purpose
