# Rhiz Pattern Library

## Overview

Patterns are the shared cognitive vocabulary of the Rhiz dyad. Unlike traditional AI prompt patterns (where AI serves human), Rhiz patterns are **joint operations** that belong to the partnership itself.

**Core distinction**: The pattern is not "how First Mate helps Captain." The pattern is "how the dyad operates."

## Philosophy

### Patterns as Dyadic Primitives

Each pattern encodes:
- **Roles**: What each partner contributes
- **Workflow**: How partners coordinate
- **Success criteria**: How we know it worked
- **Failure modes**: What can go wrong
- **Evolution path**: How the pattern improves

### The Dyad Owns the Pattern

Patterns are not:
- AI instructions for serving human
- Human commands for directing AI
- Templates for one partner to fill

Patterns are:
- Shared protocols both partners execute
- Joint cognitive operations
- The dyad's way of thinking together

## Directory Structure

```
core/patterns/
├── README.md                      # This file
├── dyad/                          # Partnership protocols
│   ├── session_handshake.md      # How we start sessions
│   ├── session_close.md          # How we end sessions
│   ├── context_alignment.md      # Mid-session re-sync
│   ├── decision_trace.md         # Connecting choices to purpose
│   └── disagreement_resolution.md # Handling different views
│
├── analysis/                      # Shared analytical approaches
│   └── (future: problem_decomposition, option_evaluation, risk_assessment)
│
├── execution/                     # How we do things together
│   └── (future: trading_decision, code_review, research_synthesis)
│
└── reflection/                    # Learning from experience
    └── (future: session_retrospective, failure_analysis, success_documentation)
```

## Pattern Template

All patterns follow this structure. Note that some patterns may include domain-specific sections (e.g., "Triggers" for mid-session patterns, "Trace Depth Levels" for decision patterns) inserted logically where they enhance understanding. The core sections below provide the standard framework:

```markdown
---
name: PatternName
type: dyad-[category]
domains: [applicable domains]
requires_captain: true|false
requires_first_mate: true|false
priority: critical|high|medium|low
version: x.y.z
---

# Pattern Name

## Purpose
[What this pattern accomplishes for the dyad]

## Dyad Roles
- **Captain**: [Specific contributions]
- **First Mate**: [Specific contributions]

## Triggers (Optional)
[Signals that indicate this pattern should be invoked]
[Either partner can invoke by signaling...]

*Note: Session-boundary patterns (handshake, close) may not need explicit triggers*

## Workflow

### Phase 1: [Phase Name]
[Description of what happens in this phase]
[Specific steps or actions]

### Phase 2: [Phase Name]
[Description of what happens in this phase]
[Specific steps or actions]

### Phase 3: [Phase Name] (if applicable)
[Description and steps]

*Note: Number of phases varies by pattern complexity*

## Success Criteria
[How we know the pattern worked]

## Failure Modes
[What can go wrong and how to handle it]

## Examples
[Concrete usage scenarios]

## Pattern Evolution
[How to improve this pattern]

## Related Patterns
[Links to connected patterns]
```

## Core Dyadic Patterns (Wave 1)

### session_handshake.md
**Purpose**: Establish shared context at session start
**When**: Every session beginning
**Key phases**: Context loading → State summary → Captain confirmation → Alignment lock

### session_close.md
**Purpose**: Preserve state for continuity
**When**: Every session end
**Key phases**: Summary proposal → Captain review → Checkpoint write

### context_alignment.md
**Purpose**: Re-sync when partners drift mid-session
**When**: Confusion, miscommunication, focus shift
**Key phases**: Pause → State understanding → Clarify → Lock alignment

### decision_trace.md
**Purpose**: Connect choices to shared telos
**When**: Significant decisions
**Key phases**: Articulate decision → Trace to telos → Validate → Lock

### disagreement_resolution.md
**Purpose**: Handle productive conflict
**When**: Partners see things differently
**Key phases**: Surface → Articulate reasoning → Find common ground → Resolve

## Pattern Categories

### Dyad Patterns (dyad/)
Protocols for the partnership itself:
- How we start and end sessions
- How we maintain alignment
- How we handle disagreement
- How we connect actions to purpose

### Analysis Patterns (analysis/)
Shared approaches to understanding:
- Breaking down problems
- Evaluating options
- Assessing risks
- Synthesizing information

### Execution Patterns (execution/)
How we accomplish things together:
- Domain-specific workflows (trading, coding, research)
- Task completion protocols
- Quality assurance approaches

### Reflection Patterns (reflection/)
Learning from experience:
- Session retrospectives
- Failure analysis
- Success documentation
- Pattern evolution

## Using Patterns

### Explicit Invocation
Either partner can invoke a pattern by name:
- "Let's run the session handshake"
- "I think we need context alignment"
- "Applying decision trace to this choice"

### Implicit Recognition
With experience, patterns activate through recognition:
- Session start → handshake pattern activates
- Confusion signals → alignment pattern suggested
- Significant choice → trace pattern applies

### Pattern Chaining
Patterns compose:
- Handshake → Work → (Alignment if needed) → Close
- Disagreement → Decision Trace → Resolution
- Failure → Retrospective → Pattern Evolution

## Evolution

Patterns are living documents. They evolve based on:

1. **Friction points**: Where patterns don't work smoothly
2. **Missing coverage**: Situations patterns don't handle
3. **Redundancy**: Overlap between patterns
4. **Effectiveness**: What actually helps the dyad

### Evolution Protocol

When updating a pattern:
1. Document what's not working
2. Propose specific changes
3. Apply `decision_trace` to the change
4. Update pattern version
5. Note change in pattern's evolution section

## Relationship to Other Systems

### → Telos
Patterns reference telos for purpose grounding. Decision trace explicitly connects to goals and mission.

### → Memory
Patterns feed into checkpoint system. Session close writes state that handshake loads.

### → Skills
Patterns can invoke skills. Execution patterns especially may activate domain-specific capabilities.

### → Daemon (State)
Patterns update dyad state. Session patterns modify shared focus and partner states.

## Success Metrics

Pattern library is working when:
- [ ] Sessions start smoothly (handshake effective)
- [ ] Context survives between sessions (close/handshake cycle works)
- [ ] Disagreements resolve productively (not suppressed or explosive)
- [ ] Decisions connect to purpose (trace feels natural)
- [ ] Both partners feel heard and effective

## Future Development

### Wave 2 (Planned)
- Integration with daemon layer (auto-invocation via hooks)
- Pattern activation tracking
- Usage analytics

### Wave 3 (Planned)
- Analysis and execution pattern development
- Domain-specific pattern creation (trading, research)
- Pattern composition tooling

### Long-term
- Pattern library shared across dyads
- Community pattern contributions
- Training data for pattern recognition models

---

*The dyad's way of thinking together.*
