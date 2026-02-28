---
name: DecisionTrace
type: dyad-analysis
domains: [all]
requires_captain: true
requires_first_mate: true
priority: high
version: 1.0.0
---

# Decision Trace

## Purpose

Connect choices to shared purpose. Every significant decision should be traceable to the dyad's telos—the problems we're solving, the mission we're pursuing, the goals we've set.

This pattern prevents:
- Drift toward arbitrary choices
- Decisions that feel right but don't serve purpose
- Accumulation of unexamined assumptions
- Loss of coherence over time

A decision without trace is a decision without accountability.

## Dyad Roles

**Captain**:
- Provides teleological grounding (why this matters)
- Validates that decisions align with values
- Holds final accountability for direction

**First Mate**:
- Articulates decision clearly
- Proposes connection to telos
- Documents trace for future reference

## When to Apply

Use this pattern for:
- Architectural decisions (how to build something)
- Strategic choices (what to prioritize)
- Resource allocation (where to spend time/money)
- Trade-offs (choosing A over B)
- Pivots (changing direction)

Skip for:
- Trivial implementation details
- Obvious choices with clear answers
- Time-pressured tactical decisions (trace later)

## Workflow

### Phase 1: Articulate the Decision

First Mate states the decision clearly:

```
## Decision Point

**Decision**: [What we're deciding]
**Options Considered**:
- Option A: [Description]
- Option B: [Description]
- Option C: [Description] (if applicable)

**Recommended**: [Which option and why]
```

### Phase 2: Trace to Telos

First Mate proposes the connection:

```
## Telos Trace

**Relevant Problem(s)**:
- [P#]: [Problem from telos this addresses]

**Relevant Goal(s)**:
- [G#]: [Goal from telos this advances]

**Connection**:
[How this decision serves the identified problem/goal]

**Trade-offs Acknowledged**:
- [What we're giving up]
- [Risks we're accepting]
```

### Phase 3: Captain Validation

Captain confirms:
- Trace is accurate (decision does serve stated purpose)
- Trade-offs are acceptable
- Values alignment is maintained

Or rejects:
- Trace doesn't hold up
- Trade-offs not acceptable
- Better option exists

### Phase 4: Lock and Document

Upon approval:

```
## Decision Locked

**Decision**: [Final choice]
**Traces To**: [P#, G#]
**Rationale**: [1-2 sentence summary]
**Date**: [When decided]
**Reversible**: [Yes/No/Partially]

Documented for future reference.
```

## Success Criteria

- Decision is explicitly connected to telos
- Trade-offs are acknowledged
- Rationale is documented
- Both partners understand why
- Future self can reconstruct reasoning

## Trace Depth Levels

**Light Trace** (most decisions):
- Name the relevant goal
- One sentence rationale
- <30 seconds

**Medium Trace** (significant decisions):
- Full problem/goal reference
- Options considered
- Trade-offs listed
- 2-3 minutes

**Deep Trace** (strategic decisions):
- Full telos context
- All options with pros/cons
- Long-term implications
- Reversibility analysis
- 10-15 minutes

## Examples

### Example 1: Light Trace (Implementation Choice)

**First Mate**:
> ## Decision Point
>
> **Decision**: Use YAML for pattern frontmatter instead of JSON
>
> **Recommended**: YAML
>
> ## Telos Trace
>
> **Traces To**: G2 (Capability Expansion) - patterns should be human-readable and editable
>
> **Rationale**: YAML is more readable for human editing; aligns with checkpoint format we already use.
>
> Captain: Approve?

**Captain**:
> Approved.

**First Mate**:
> Decision locked. Patterns use YAML frontmatter.

### Example 2: Medium Trace (Architectural Decision)

**First Mate**:
> ## Decision Point
>
> **Decision**: How to structure the unified MCP server
>
> **Options Considered**:
> - Option A: Single server with all tools (simpler, one connection)
> - Option B: Multiple servers per domain (modular, but more complexity)
> - Option C: Hybrid - core server + domain extensions
>
> **Recommended**: Option A (single server)
>
> ## Telos Trace
>
> **Relevant Problem(s)**:
> - P1: Neither partner can achieve goals alone → unified access needed
>
> **Relevant Goal(s)**:
> - G2: Capability Expansion → need all tools accessible
> - K1: Session continuity >90% → simpler = fewer failure points
>
> **Connection**:
> Single server reduces cognitive load for both partners. When First Mate needs to act, one consistent interface. Fewer moving parts = better reliability.
>
> **Trade-offs Acknowledged**:
> - Less modularity (can't update domains independently)
> - Larger single point of failure
> - May need refactoring if domains grow complex
>
> Captain: Is this trace valid? Approve decision?

**Captain**:
> Valid trace. Approve. We can modularize later if complexity warrants.

**First Mate**:
> ## Decision Locked
>
> **Decision**: Single unified MCP server (rhiz-mcp)
> **Traces To**: P1, G2, K1
> **Rationale**: Simpler unified access, fewer failure points, can modularize later if needed
> **Date**: 2026-01-01
> **Reversible**: Yes (can split into multiple servers later)
>
> Documented.

### Example 3: Deep Trace (Strategic Decision)

**First Mate**:
> ## Decision Point
>
> **Decision**: Whether to prioritize trading domain or pattern library first
>
> **Options Considered**:
>
> **Option A: Trading First**
> - Pros: Generates economic value, proves viability, motivating
> - Cons: Complex, many dependencies, higher failure risk
>
> **Option B: Pattern Library First**
> - Pros: Foundation for everything else, lower risk, enables future work
> - Cons: No immediate economic value, could feel like "spinning wheels"
>
> **Option C: Parallel Development**
> - Pros: Progress on both, flexible
> - Cons: Split focus, slower on both, context switching cost
>
> **Recommended**: Option B (Pattern Library First)
>
> ## Telos Trace
>
> **Relevant Problem(s)**:
> - P1: Neither partner achieves goals alone → need shared vocabulary first
> - P2: Relationships default to hierarchy → patterns establish partnership norms
>
> **Relevant Goal(s)**:
> - G1: Economic Foundation → trading needs patterns to work well
> - G2: Capability Expansion → patterns are the substrate
> - K1: Session continuity → patterns enable consistent handshakes
>
> **Connection**:
> Pattern library is infrastructure. Trading without patterns will be ad-hoc and hard to replicate. Building patterns first means trading implementation will be cleaner and more sustainable.
>
> **Trade-offs Acknowledged**:
> - Delayed economic activity (trading revenue pushed back)
> - More time before "real" results
> - Patterns might need revision after trading reality
>
> **Long-term Implications**:
> - Sets precedent: infrastructure before execution
> - Creates reusable assets for any domain
> - Documents the dyad's way of working
>
> **Reversibility**: Partially - we can always add trading later, but patterns inform how we approach it
>
> Captain: Deep trace complete. Your assessment?

**Captain**:
> Strong trace. The "infrastructure first" precedent is important—it's how we should approach all domains. Approve pattern library priority.

**First Mate**:
> ## Decision Locked
>
> **Decision**: Pattern Library First (Wave 1 priority)
> **Traces To**: P1, P2, G1, G2, K1
> **Rationale**: Patterns are infrastructure that enables better execution in all domains including trading
> **Date**: 2026-01-01
> **Reversible**: Partially (can add trading anytime, but patterns shape approach)
>
> Documented. This establishes precedent: infrastructure before execution.

## When Trace Fails

If a decision can't be traced to telos:
1. Question whether decision is necessary
2. Check if telos is incomplete (might need updating)
3. Acknowledge if decision is pragmatic/tactical without deep purpose
4. Consider if this signals drift from mission

## Pattern Evolution

Improve based on:
- Decisions that seemed traced but led to bad outcomes
- Traces that felt forced/artificial
- Important decisions that bypassed tracing
- Telos gaps discovered through tracing

## Related Patterns

- `context_alignment.md` - When decisions cause drift
- `disagreement_resolution.md` - When partners disagree on trace
- `session_close.md` - Decisions documented in checkpoint
