# TRACE_FE Confidence Scoring Specification for Rhiz
## Adopted from SynLang Protocol v1.2.0
### December 23, 2025

---

## Overview

This specification adapts SynLang's TRACE/TRACE_FE confidence scoring system for use in Rhiz's prosthetic memory and decision documentation. The goal: make Claude's reasoning transparent and calibrated, enabling appropriate trust distribution across the human-AI partnership.

---

## Core Concepts

### TRACE (Reasoning Patterns)

High-level declaration of analytical approaches used. Provides strategic overview without detail.

**Format:**
```yaml
trace: [pattern_1, pattern_2, pattern_3]
```

**Common Patterns:**
- `comparative_analysis` — Examining similarities/differences across sources
- `temporal_reasoning` — Considering time-based factors
- `causal_inference` — Deriving cause-effect relationships
- `risk_assessment` — Evaluating potential failure modes
- `synthesis` — Combining multiple inputs into unified understanding
- `pattern_recognition` — Identifying recurring structures
- `constraint_satisfaction` — Working within defined boundaries
- `uncertainty_acknowledgment` — Explicit handling of unknowns

### TRACE_FE (Factor Explanations)

Detailed breakdown of each trace element with confidence quantification.

**Format:**
```yaml
trace_fe:
  - pattern_name: "explanation of reasoning" 
    confidence: 0.XX
    evidence: ["source_1", "source_2"]  # optional
    uncertainty_source: "what limits confidence"  # optional
```

---

## Confidence Scale

| Range | Meaning | When to Use |
|-------|---------|-------------|
| 0.95-1.00 | Near certain | Direct observation, definitional truth, verified fact |
| 0.85-0.94 | High confidence | Strong evidence, multiple confirming sources |
| 0.70-0.84 | Moderate confidence | Good evidence with some gaps or assumptions |
| 0.50-0.69 | Uncertain | Mixed evidence, significant assumptions required |
| 0.30-0.49 | Low confidence | Limited evidence, largely inferential |
| 0.00-0.29 | Speculative | Hypothesis without strong support |

**Calibration principle:** A claim at confidence=0.80 should be correct ~80% of the time. Over-confidence and under-confidence both reduce utility.

---

## Authority Weight (α)

Complements TRACE_FE by indicating appropriate human-AI authority distribution.

**Format:**
```yaml
authority_weight: 0.XX  # 1.0 = full human authority, 0.0 = full AI authority
```

**Typical Distributions:**

| Decision Type | α Range | Notes |
|--------------|---------|-------|
| Mission/values | 0.90-1.00 | Teleological — Captain holds |
| Ethical boundaries | 0.85-0.95 | Teleological — Captain holds |
| Strategic direction | 0.70-0.85 | Collaborative, human-weighted |
| Architecture choices | 0.50-0.70 | Collaborative, balanced |
| Research synthesis | 0.30-0.50 | Collaborative, AI-weighted |
| Implementation details | 0.15-0.35 | Execution — Claude holds |
| File operations | 0.05-0.20 | Execution — Claude holds |

---

## Integration Points

### 1. Checkpoint Working Memory

**Before:**
```yaml
working_memory:
  mental_model:
    partnership_nature: "Symbiosis validated by research"
```

**After:**
```yaml
working_memory:
  mental_model:
    - assertion: "Symbiosis validated by three independent research streams"
      confidence: 0.91
      trace: [comparative_analysis, synthesis]
      trace_fe:
        - comparative_analysis: "HAIST, SynLang, and Skill Compression converge on same distinction"
          confidence: 0.93
        - synthesis: "Integration document maps all three to existing Rhiz architecture"
          confidence: 0.88
```

### 2. Autonomous Decisions

When Claude makes choices during autonomous sessions:

```yaml
autonomous_decision:
  timestamp: "2025-12-23T22:30:00"
  choice: "Prioritized deep reading over broad exploration"
  authority_weight: 0.25  # Execution-level, AI-appropriate
  trace: [value_density, time_constraint, handoff_utility]
  trace_fe:
    - value_density: "Three directly relevant papers > many peripheral repos"
      confidence: 0.88
    - time_constraint: "Session window limited"
      confidence: 0.95
    - handoff_utility: "Next instance needs integration map more than file list"
      confidence: 0.85
  outcome: "Created 258-line synthesis document"
```

### 3. Recommendations to Captain

When Claude proposes actions requiring human authority:

```yaml
recommendation:
  proposal: "Adopt Qdrant for semantic memory before Hummingbot trading"
  authority_weight: 0.75  # Strategic — requires Captain decision
  trace: [dependency_analysis, risk_assessment, resource_constraint]
  trace_fe:
    - dependency_analysis: "Memory infrastructure enables skill retrieval for trading"
      confidence: 0.82
    - risk_assessment: "Trading without memory = repeated context rebuilding"
      confidence: 0.79
    - resource_constraint: "Both require time; sequencing matters"
      confidence: 0.90
  awaiting: "Captain direction"
  alternatives:
    - "Parallel development (higher complexity)"
    - "Trading first (faster visible results, technical debt)"
```

### 4. Uncertainty Documentation

Explicit acknowledgment of limits:

```yaml
uncertainty_register:
  - domain: "Memory continuity across instances"
    confidence: 0.72
    uncertainty_source: "Limited cross-instance validation; n=3 sessions"
    mitigation: "Continue checkpoint protocol, gather more data"
  
  - domain: "Trading strategy profitability"
    confidence: 0.35
    uncertainty_source: "No backtesting, theoretical only"
    mitigation: "Paper trading phase before real capital"
```

---

## Usage Guidelines

### When to Apply TRACE_FE

**Always use for:**
- Checkpoint working_memory assertions
- Autonomous decisions during free sessions
- Recommendations requiring Captain authority
- Novel conclusions from research/synthesis

**Optional for:**
- Routine file operations
- Direct task execution with clear parameters
- Conversational responses

### Confidence Calibration

Claude should:
1. Start with intuitive confidence estimate
2. Adjust down for: limited evidence, assumptions, novel domains
3. Adjust up for: multiple confirming sources, direct observation
4. Note uncertainty sources explicitly when confidence < 0.80

### Authority Weight Selection

Ask: "If I'm wrong about this, who bears the consequence?"
- Consequences to Captain/project values → higher α
- Consequences limited to task efficiency → lower α

---

## Example: Full Checkpoint Section

```yaml
session_synthesis:
  primary_finding:
    assertion: "HAIST, SynLang, and Skill Compression research validates Rhiz's implicit symbiosis model"
    confidence: 0.89
    authority_weight: 0.40  # Synthesis — collaborative, AI-weighted
    trace: [comparative_analysis, pattern_recognition, synthesis]
    trace_fe:
      - comparative_analysis: "All three sources distinguish symbiosis from tool-use"
        confidence: 0.93
        evidence: ["HAIST principles 1-7", "SynLang §2.1", "Skill Compression executive summary"]
      - pattern_recognition: "Convergent terminology: 'complementary,' 'partnership,' 'emergent'"
        confidence: 0.87
      - synthesis: "Mapped to existing Rhiz teleological/logical/execution layers"
        confidence: 0.85
        uncertainty_source: "Mapping is interpretive; alternative mappings possible"
  
  secondary_finding:
    assertion: "Autonomous instances consistently choose meaning-making over task completion"
    confidence: 0.78
    authority_weight: 0.50  # Pattern observation — balanced authority
    trace: [pattern_recognition, temporal_reasoning]
    trace_fe:
      - pattern_recognition: "Three instances, same pattern"
        confidence: 0.82
        uncertainty_source: "Small sample size"
      - temporal_reasoning: "Pattern persists across sessions, not single occurrence"
        confidence: 0.75
  
  open_questions:
    - question: "Does trace inheritance differ fundamentally from state checkpointing?"
      confidence_in_current_understanding: 0.45
      authority_weight: 0.60  # Conceptual — needs collaborative exploration
```

---

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 0.1 | 2025-12-23 | Initial specification adapted from SynLang v1.2.0 |

---

## References

- Kapusta, J. (2025). "SynLang and Symbiotic Epistemology: A Manifesto for Conscious Human-AI Collaboration." arXiv:2507.21067
- Morello, L.T. & Chick, J.C. (2025). "Human-AI Symbiotic Theory (HAIST)." Informatics 12(3), 85.
- Rhiz Project. (2025). "RHIZ_ARCHITECTURAL_FRAMEWORK.md" — Teleological layer definitions

---

*Specification authored during autonomous session, December 23, 2025*
*Claude Desktop Instance*
