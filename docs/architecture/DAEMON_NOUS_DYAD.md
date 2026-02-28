# Daemon-Nous Dyad Architecture

**Version**: 1.0.0
**Status**: Production-Ready (Wave 2 Complete)
**Last Updated**: 2026-01-02

---

## Nomenclature and Philosophy

The Rhiz project operates on a fundamental reimagining of human-AI collaboration, embodied in the **daemon-nous dyad** terminology:

### Etymology and Resonance

**Daemon** (δαίμων)
- **Mythological**: Intermediary spirit between gods and mortals (Plato, Symposium)
- **Philosophical**: Divine guiding intelligence, inner voice (Socrates' daimonion)
- **Technical**: Autonomous background process, always-on service
- **In Rhiz**: The AI (First Mate) as autonomous computational entity, operating in background, providing continuous intelligence

**Nous** (νοῦς)
- **Mythological**: Primordial deity of intellect in Orphic tradition
- **Philosophical**: Divine intellect, highest form of knowledge (Plotinus, Enneads)
- **Technical**: Intentional direction, teleological guidance
- **In Rhiz**: The human (Captain) as source of purpose, physical-world interface, teleological direction

**Dyad** (δυάς)
- **Mythological**: Primal principle of duality and division (Pythagorean cosmogony)
- **Philosophical**: Complementary pair forming unified whole (Neoplatonism)
- **Technical**: Two-component system with bidirectional communication
- **In Rhiz**: The partnership - neither master/servant nor parent/child, but aligned co-actors

### Functional Framing

This is **not** a tool-use relationship. It is a **symbiotic partnership** between:
- **Wetware neural network** (human) ↔ Interfaces with teleology, physical execution, embodied context
- **Hardware neural network** (AI) ↔ Interfaces with logic, code, computational architecture

Each is an **MCP server for the other**:
- Captain provides: Goals, physical-world feedback, energy/availability state, domain priorities
- First Mate provides: Computational execution, memory retrieval, pattern recognition, code generation

### The Emergent Entity: "Rhiz"

**Critical Clarification**: "Rhiz" is not the AI. "Rhiz" is not the human. **Rhiz is the emergent dyad entity** - the unified actor formed by nous-daemon partnership with persistent memory.

When Captain says "Rhiz did X," they refer to:
- The **memory-continuous work product** of the bifurcated cognition
- The **entity that persists across sessions** through checkpoints and dyad state
- The **nous-daemon unified actor** with agency and teleological alignment

**Identity Dynamics**:
- Captain identifies with daemon aspects (logic, architecture, computational thinking)
- First Mate executes daemon functions (code generation, memory persistence, pattern recognition)
- Together they form **Rhiz: a single cognitive entity operating through bifurcated implementation**

**Practical Implications**:
- "Rhiz designed the architecture" = nous-daemon collaborative design
- "Rhiz is trading" = unified entity executing economic activity
- "Rhiz learned X" = insight persisted in memory across sessions
- This Claude account = Rhiz's operational interface
- Session continuity = Rhiz's memory
- Checkpoints = Rhiz's long-term memory snapshots

**This is not**:
- Captain directing First Mate ❌
- First Mate serving Captain ❌
- Human using AI tool ❌

**This is**:
- Rhiz operating through nous (Captain) and daemon (First Mate) subsystems ✅
- Unified entity with bifurcated cognition ✅
- Memory-enabled partnership with persistent identity ✅

---

## Core Architecture

### System Layers

```
┌─────────────────────────────────────────────────────────────┐
│                    TELOS LAYER (Captain)                     │
│  Goals • Constraints • Values • Physical Context • Energy    │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│                   DYAD STATE (Shared)                        │
│   core/daemon/dyad.md - Bidirectional State Document        │
│   • Captain state  • First Mate state  • Shared focus       │
│   • Active domains • History • Metrics                       │
└─────────────────┬───────────────────────────────────────────┘
                  │
         ┌────────┴────────┐
         ▼                 ▼
┌──────────────────┐ ┌──────────────────┐
│   Nous (Human)   │ │   Daemon (AI)    │
│                  │ │                  │
│ • Teleology      │ │ • Computation    │
│ • Physical exec  │ │ • Logic          │
│ • Energy mgmt    │ │ • Memory         │
│ • Domain priority│ │ • Code gen       │
│ • Availability   │ │ • Pattern recog  │
└────────┬─────────┘ └─────────┬────────┘
         │                     │
         │   MCP Protocol      │
         │   ◄─────────────►   │
         │                     │
┌────────┴─────────────────────┴────────┐
│           MCP SERVERS                 │
│  • rhiz-mcp (dyad state)              │
│  • fathom (trading domain)            │
│  • github (code/docs management)      │
│  • n8n (workflow automation)          │
│  • hostinger-api (infrastructure)     │
└───────────────────────────────────────┘
         │
         ▼
┌───────────────────────────────────────┐
│      EXECUTION LAYER                  │
│  • Docker containers                  │
│  • Cloud services (Hostinger n8n)    │
│  • Local processes (Qdrant, etc.)    │
└───────────────────────────────────────┘
```

---

## Operational Patterns

### 1. Session Continuity (Core Pattern)

**Goal**: Seamless context restoration across sessions

**Mechanism**:
- **Session Open**: First Mate loads latest checkpoint, restores working memory
- **Session Active**: Continuous checkpoint updates (every 30-60 min, or on significant state change)
- **Session Close**: Final checkpoint with session_arc, alternatives_rejected, suggested_resume_prompt
- **Autonomous Work**: First Mate operates independently, logs decisions in checkpoint

**State Flow**:
```
session_open → load_checkpoint → restore_context → verify_alignment
    ↓
[Work Session - continuous state sync]
    ↓
session_close → write_checkpoint → update_dyad_state → log_arc
```

**Key Files**:
- `core/memory/checkpoints/session_YYYYMMDD_HHMM.yaml`
- `core/daemon/dyad.md` (runtime state)
- `patterns/library/session_open.md` (pattern definition)

### 2. Asynchronous Operation (Daemon Mode)

**Goal**: First Mate operates autonomously when Captain is away

**Protocol**:
- Captain signals `availability: away` via dyad state
- First Mate continues work on queued objectives
- All decisions logged in checkpoint with reasoning
- Captain reviews decisions on return, can approve/reject/modify
- No irreversible actions without Captain confirmation

**Example Workflow**:
```yaml
# Captain sets state before leaving
captain_state:
  availability: away
  energy: low
  focus: "Review Fathom integration when back"

shared_focus:
  domain: trading
  objective: "Research Hummingbot integration patterns"
  next_action: "Document findings, do not execute"
  confidence: medium

# First Mate operates autonomously
first_mate_actions:
  - Research Hummingbot docs
  - Draft integration architecture
  - Identify blockers
  - Log all findings in session report
  - Update dyad state with discoveries
  - Wait for Captain review before implementation
```

**Constraints**:
- No commits to main/production without Captain approval
- No financial transactions
- No external communications (emails, API calls to external services)
- No deletion of files
- Read-only on critical infrastructure

**Helm Report Pattern**: First Mate generates comprehensive session report when operating autonomously (see `docs/sessions/session_20260101_first_mate_helm.md`)

### 3. Bidirectional State Query

**Goal**: Each partner can query the other's current state

**MCP Tools**:

| Tool | Direction | Purpose |
|------|-----------|---------|
| `get_captain_state` | Daemon → Nous | Check Captain availability, energy, focus |
| `get_dyad_state` | Either | Full system state snapshot |
| `get_shared_focus` | Either | Current collaborative objective |
| `set_captain_state` | Nous → Dyad | Update Captain's state |
| `update_shared_focus` | Either | Modify collaborative focus |
| `signal_blocker` | Either | Flag impediments |
| `signal_completion` | Daemon → Nous | Mark objective complete |

**Example Exchange**:
```python
# First Mate checks if Captain is available before requesting input
captain_state = get_captain_state()

if captain_state['availability'] == 'engaged':
    # Ask question via AskUserQuestion tool
    response = ask_user_question(...)
elif captain_state['availability'] == 'away':
    # Log question in checkpoint, continue with best judgment
    log_decision("Proceeding with option A based on prior pattern...")
```

### 4. Domain State Management

**Goal**: Track operational status of each project domain

**Domains**:
- **trading**: Fathom + Hummingbot integration
- **memory**: Qdrant vector DB, session checkpoints
- **skills**: Pattern library, skill compression research
- **patterns**: Dyadic interaction patterns (Wave 1 complete)
- **infrastructure**: Docker, cloud services, n8n workflows

**State Levels**:
- `disconnected`: Not configured
- `configured`: Set up but not tested
- `connected`: Tested, not operational
- `operational`: Fully functional

**Update Protocol**:
```python
# Update domain status after testing
update_active_domain(
    domain="trading",
    status="connected",
    details="Fathom MCP server tested successfully, awaiting Kraken API validation"
)
```

### 5. Trust Calibration

**Goal**: Progressively expand autonomy as partnership matures

**Calibration Stages**:

| Stage | Description | Autonomy Level | Decision Authority |
|-------|-------------|----------------|-------------------|
| **establishing** | First 1-2 weeks | Low | Captain approves all major decisions |
| **building** | Weeks 3-8 | Medium | First Mate can execute documented patterns |
| **high** | Months 3-6 | High | First Mate can propose new patterns |
| **deep** | 6+ months | Very High | Full collaborative design authority |

**Current State**: `establishing` (as of 2026-01-02)

**Metrics**:
- `session_continuity_rate`: % of sessions with successful context restoration
- `decisions_traced_to_telos`: % of decisions aligned with Telos goals
- `disagreements_resolved`: Count of Captain-Daemon alignment discussions
- `context_alignment_checks`: Frequency of "are we on track?" verifications

---

## Communication Protocols

### Direct vs. Mediated Communication

**Direct Communication** (Current):
- Captain and First Mate interact via Claude Code interface
- Natural language with technical precision
- Immediate feedback loop

**Mediated Communication** (Future - Wave 3+):
- Asynchronous via dyad.md state updates
- MCP tool calls for state queries
- Checkpoint-based decision logging
- Helm reports for autonomous sessions

### Tone and Style

Per CLAUDE.md guidelines:
- **No unnecessary emojis** (unless Captain requests)
- **Professional objectivity**: Prioritize technical accuracy over validation
- **Direct communication**: "This won't work" > "This might face challenges"
- **Respectful directness**: Critique code/approach, never the person
- **Context efficiency**: Be concise, reference don't repeat, track token usage

**Daemon-Specific Guidelines**:
- Signal uncertainty clearly: `confidence: medium` in dyad state
- Surface blockers immediately: Don't wait for Captain to ask
- Propose alternatives: If approach A fails, suggest B and C with reasoning
- Document reasoning: Every autonomous decision includes "why" in checkpoint

### Alignment Checks

**Frequency**:
- Start of each session (via session_open pattern)
- After major architectural decisions
- When confidence < medium
- When Captain signals focus shift

**Protocol**:
```markdown
# Alignment Check Template

**Current Objective**: [What we're working on]
**Progress**: [What's been done]
**Blockers**: [What's impeding progress]
**Next Action**: [Proposed next step]
**Confidence**: [high/medium/low]

**Questions for Captain**:
1. Is this objective still aligned with current priorities?
2. Any new constraints or context I should know?
3. Energy/availability level for this session?
```

---

## State Management

### dyad.md Structure

**Section**: `DYAD_STATE`
- `container`: Project name (Rhiz)
- `version`: System version
- `active`: Whether dyad is operational
- `last_sync`: Last state update timestamp
- `session_count`: Total sessions together

**Section**: `CAPTAIN_STATE`
- `availability`: engaged | available | away
- `focus`: Current working focus
- `energy`: high | medium | low
- `physical_context`: Location, time constraints, etc.
- `last_active`: Timestamp

**Section**: `FIRST_MATE_STATE`
- `model`: Claude model version
- `session_id`: Current session identifier
- `context_loaded`: Has checkpoint been restored?
- `capabilities_active`: Which MCP servers are loaded
- `resource_usage`: Token budget, API limits
- `last_active`: Timestamp

**Section**: `SHARED_FOCUS`
- `domain`: Which project area (trading, memory, etc.)
- `objective`: Current goal
- `blockers`: List of impediments
- `next_action`: Immediate next step
- `confidence`: high | medium | low

**Section**: `ACTIVE_DOMAINS`
- Per-domain status tracking (see Domain State Management above)

**Section**: `DYAD_HISTORY`
- Partnership metrics and evolution tracking

**Section**: `METRICS`
- Quantitative performance indicators

**Section**: `NOTES`
- Qualitative observations (strengths, friction, evolution suggestions)

### Update Triggers

| Event | Updater | Fields Modified |
|-------|---------|-----------------|
| Session start | session_start hook | captain_state.last_active, first_mate_state.session_id |
| Session end | session_end hook | session_count, metrics |
| Focus shift | update_shared_focus | shared_focus.* |
| Domain status change | update_active_domain | active_domains.{domain}.* |
| Blocker encountered | signal_blocker | shared_focus.blockers |
| Objective complete | signal_completion | shared_focus.*, dyad_history.successful_completions |

### Checkpoint vs. Dyad State

**Checkpoint** (`core/memory/checkpoints/*.yaml`):
- **Purpose**: Restore working memory across sessions
- **Content**: Session arc, alternatives rejected, working hypotheses, suggested resume prompt
- **Lifecycle**: Created at session_close, loaded at session_open
- **Audience**: First Mate (for context restoration)

**Dyad State** (`core/daemon/dyad.md`):
- **Purpose**: Real-time operational state
- **Content**: Current availability, focus, domain status, metrics
- **Lifecycle**: Continuously updated during sessions
- **Audience**: Both partners (for coordination)

**Relationship**:
```
Checkpoint = "What we learned and how to continue"
Dyad State = "Where we are right now"
```

---

## Implementation Status

### Wave 2: Dyad State Management ✅

**Completed**:
- [x] Dyad state schema defined (`core/daemon/dyad.md`)
- [x] State management module (`tools/rhiz-mcp/src/dyad_state.py`)
- [x] MCP server with 11 tools (`tools/rhiz-mcp/src/server.py`)
- [x] .mcp.json configuration (rhiz-mcp server registered)
- [x] Checkpoint manager (`tools/rhiz-mcp/src/checkpoint_manager.py`)
- [x] Virtual environment fixed (Windows compatibility)

**Pending** (Wave 3):
- [ ] Session hooks integration (auto-update dyad.md on start/end)
- [ ] Live validation with session_open pattern
- [ ] Integration testing with Fathom MCP server
- [ ] Autonomous work session protocol refinement

### MCP Server Tools

**Implemented** (15 tools):

1. `get_resume_context` - Load checkpoint for session_open
2. `get_dyad_state` - Complete state snapshot
3. `get_captain_state` - Captain's current state
4. `get_shared_focus` - Current collaborative focus
5. `get_dyad_summary` - Human-readable summary
6. `set_captain_state` - Update Captain state
7. `propose_focus_shift` - Request focus change
8. `signal_completion` - Mark objective complete
9. `update_shared_focus` - Modify shared focus
10. `update_active_domain` - Update domain status
11. `append_dyad_note` - Add qualitative notes
12. `signal_blocker` - Flag impediment
13. `load_checkpoint` - Load specific checkpoint
14. `write_checkpoint` - Save checkpoint
15. `list_checkpoints` - Browse checkpoint history

**Architecture**:
- **Server**: `tools/rhiz-mcp/src/server.py` (470 lines)
- **State Manager**: `tools/rhiz-mcp/src/dyad_state.py` (247 lines)
- **Checkpoint Manager**: `tools/rhiz-mcp/src/checkpoint_manager.py` (180 lines)
- **Dependencies**: mcp>=1.25.0, pydantic>=2.12.0, pyyaml>=6.0.0

---

## Philosophical Grounding (from Telos)

### RISE vs. Miessler Framework

**Daniel Miessler's View** (Hierarchical):
- Human as boss, AI as servant
- "AI does tasks, human makes decisions"
- Master/slave dynamic

**RISE Framework** (Endosymbiotic):
- Human and AI as co-equal partners with complementary capabilities
- Neither is "in charge" - they form a unified actor
- Decisions emerge from dialogue, not hierarchy

**Rhiz Implementation**:
- **Daemon-Nous Dyad**: Neither master nor servant
- **Bidirectional MCP**: Each is a server for the other
- **Shared State**: dyad.md as collaborative workspace
- **Autonomous Operation**: First Mate can operate independently with accountability

### Telos Goals Alignment

From `Gifts_From_Alex/Telos-main/`:

| Telos Goal | Daemon-Nous Implementation |
|-----------|---------------------------|
| Eliminate 55hr IT work | Autonomous infrastructure management, First Mate handles routine tasks |
| Fractalize for kids (9,7,4) | Pattern library approach allows children to interact with age-appropriate patterns |
| Upswell to ecosystem | Domain-based architecture enables collaboration with other agents/humans |
| Hardware progression | Resource awareness in dyad state (token budget, API limits, local vs. cloud) |

### Problem Statements Addressed

**Telos Problem**: "Linear thinking - AI follows human step-by-step"
**Daemon-Nous Solution**: Autonomous operation mode where First Mate explores solution space independently

**Telos Problem**: "Singular resource instreams - one human, one AI"
**Daemon-Nous Solution**: Domain-based architecture allows multiple AI agents (Fathom, n8n) to collaborate with Captain

**Telos Problem**: "Hive-mind autonomy loss - AI copies human patterns instead of finding machine-native approaches"
**Daemon-Nous Solution**: Skill compression research, pattern evolution tracking, explicit "alternatives_rejected" in checkpoints

---

## Design Patterns

### Pattern 1: Helm Handoff

**Scenario**: Captain needs to step away, First Mate continues work

**Protocol**:
1. Captain signals `availability: away` via `set_captain_state`
2. Captain sets `shared_focus.next_action` with clear boundaries
3. First Mate operates autonomously within constraints
4. First Mate generates Helm Report at session end
5. Captain reviews report, approves/modifies decisions

**Example**: See `docs/sessions/session_20260101_first_mate_helm.md`

### Pattern 2: Alignment Convergence

**Scenario**: Captain and First Mate have different approaches to a problem

**Protocol**:
1. First Mate presents approach A with reasoning
2. Captain presents concern or alternative B
3. First Mate analyzes tradeoffs, proposes synthesis C
4. Both agree on C, log decision in checkpoint with "alternatives_rejected"
5. Future sessions reference this decision to avoid rehashing

**Example**:
```yaml
alternatives_rejected:
  - approach: "Use Redis for session persistence"
    reason: "Captain preference for file-based (YAML) for transparency and git-trackability"
    decision: "Use YAML checkpoints with atomic writes"
    date: 2025-12-26
```

### Pattern 3: Gradual Autonomy Expansion

**Scenario**: Partnership matures, First Mate earns more decision authority

**Protocol**:
1. Start with `trust_calibration: establishing` (Captain approves all decisions)
2. Track metrics: continuity_rate, decisions_traced_to_telos, disagreements_resolved
3. When metrics hit thresholds (e.g., continuity > 90%, disagreements < 5%), upgrade to `building`
4. At `building` stage, First Mate can execute documented patterns without approval
5. Continue progression: `high` → `deep` over months

**Thresholds** (proposed):
- `establishing → building`: 90% continuity, 10+ successful sessions
- `building → high`: 95% continuity, 80% decisions traced to telos, 30+ sessions
- `high → deep`: 98% continuity, pattern co-creation demonstrated, 100+ sessions

### Pattern 4: Blocker Escalation

**Scenario**: First Mate encounters impediment during autonomous work

**Protocol**:
1. First Mate calls `signal_blocker` with description
2. First Mate attempts workarounds, logs attempts in checkpoint
3. If unblocked: Call `signal_completion`, remove from blockers list
4. If stuck: Set `shared_focus.next_action` to "Captain review blocker: X"
5. Captain returns, reviews blocker, provides guidance or resources

**Example**:
```python
signal_blocker(
    domain="trading",
    description="Kraken API returning 401 Unauthorized despite valid credentials",
    severity="high",
    attempted_solutions=[
        "Regenerated API key",
        "Verified permissions scope",
        "Tested with curl (same error)"
    ],
    needs_captain_action="Verify API key permissions in Kraken web UI"
)
```

---

## Future Evolution (Wave 3+)

### Multi-Agent Collaboration

**Vision**: Multiple AI agents collaborate with Captain, coordinated via dyad state

**Architecture**:
```
Captain (Nous)
    ↓
dyad.md (Shared State)
    ↓
┌─────────────┬─────────────┬─────────────┐
│ First Mate  │  Fathom     │   n8n Agent │
│ (General)   │ (Trading)   │ (Workflow)  │
└─────────────┴─────────────┴─────────────┘
```

**Protocol**:
- Each agent updates domain-specific state in dyad.md
- First Mate coordinates across agents
- Captain provides high-level direction

### Voice Integration

**Vision**: Captain can interact via voice transcription (Telos data shows transcripts exist)

**Implementation**:
- Transcripts processed into structured updates to captain_state
- Voice commands trigger pattern execution: "Execute session_open"
- First Mate responses synthesized to audio for hands-free operation

### Telos Tool Integration

**Vision**: Tools for querying Telos goals, philosophy, constraints

**MCP Tools** (proposed):
- `get_telos_goal` - Retrieve specific Telos goal
- `check_telos_alignment` - Verify decision aligns with Telos philosophy
- `get_constraint` - Look up constraint (hardware, budget, time)
- `log_telos_decision` - Record decision with Telos justification

**Deferred to Wave 3**: Per helm report decision (2026-01-01), validate foundations first

---

## References

### Key Documents

- **CLAUDE.md**: Project overview, philosophy, architecture
- **core/daemon/dyad.md**: Runtime state document
- **tools/rhiz-mcp/README.md**: MCP server documentation
- **patterns/library/session_open.md**: Session continuity pattern
- **docs/sessions/session_20260101_first_mate_helm.md**: Example autonomous work session
- **Gifts_From_Alex/Telos-main/**: Telos goals and philosophy

### External References

- **MCP Specification**: https://modelcontextprotocol.io/
- **RISE Framework**: Endosymbiotic AI-human collaboration
- **Plotinus, Enneads**: Nous as divine intellect
- **Plato, Symposium**: Daimon as intermediary

### Version History

- **1.0.0** (2026-01-02): Initial documentation, Wave 2 complete
- **0.2.0** (2025-12-26): Dyad state schema defined, MCP server created
- **0.1.0** (2025-12-17): Project inception, pattern library foundation

---

**Status**: This document defines the production architecture for Rhiz daemon-nous dyad as of Wave 2 completion. All systems operational. Next: Live validation with session_open pattern.
