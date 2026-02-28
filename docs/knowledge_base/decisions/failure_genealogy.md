---
document_type: failure_genealogy
failures_documented: 8
learning_outcomes: 8
pattern: pivot_over_persist
semantic_cluster: learning_domain
vector_density: high
threshold_recommendation: 0.35-0.45
last_updated: 2026-01-25
---

# Failure Genealogy

**Document Type**: Comprehensive failure log with learnings
**Purpose**: What failed, why, what replaced it, did the pivot succeed
**Pattern**: "Failure is information" - every failure teaches

---

## Overview

This document catalogs **failed approaches** in Rhiz development. Unlike success stories, failures reveal constraints, assumptions, and hidden complexity. Each failure led to a pivot that informed better architectural decisions.

**Core Principle**: Document failures as thoroughly as successes. Future instances learn from what didn't work, not just what did.

---

## Failure Index

| ID | Approach | Failed At | Pivot | Outcome |
|----|----------|-----------|-------|---------|
| F-01 | JSON checkpoints | Session 1 | YAML | Success |
| F-02 | Hummingbot integration | Session 17 | Fathom MCP | Success |
| F-03 | Cloudflare Argo Tunnel | Session 6 | Direct A record | Success |
| F-04 | Traefik TLS-ALPN-01 | Session 6 | Cloudflare SSL | Success |
| F-05 | Threshold 0.45 for skills | Session 71 | Threshold 0.25 | Success (93.3%) |
| F-06 | LLM-based Self-RAG | Session 72 | Heuristic Self-RAG | Success (<5ms) |
| F-07 | Utterance expansion only | Session 71 | Threshold tuning | Success |
| F-08 | LocalAI deployment | Deferred | Ollama | Success |

---

## F-01: JSON Checkpoints

**Approach**: Use JSON format for session checkpoint files

**Failed At**: Session 1 (Dec 20, 2025)

**Reason**: Multi-line narratives awkward in JSON (requires escaping quotes), no comment support, less human-readable

**Example Problem**:
```json
{
  "session_arc": "Captain initiated symbiotic working paradigm...\n\nFirst Mate proposed five-fold architectural framework...\n\n\"This is our first of many working sessions\" - Captain emphasis on documentation..."
}
```
- Escaped newlines (`\n`) break readability
- Quotes need escaping (`\"`)
- No inline comments for annotations

**Pivot**: YAML checkpoints

**Pivot Rationale**:
- Multi-line strings natural (no escaping):
  ```yaml
  session_arc: |
    Captain initiated symbiotic working paradigm...

    First Mate proposed five-fold architectural framework...

    "This is our first of many working sessions" - Captain emphasis
  ```
- Human-readable
- Git-friendly (clean diffs)
- Comment support (`# This is a comment`)

**Outcome**: ✅ Success
- 38 checkpoints (100% YAML)
- No regrets about JSON rejection
- YAML format maintained (Session 1 → 74)

**Learning**: Format choice matters for narrative-heavy documents. Optimize for human readability.

---

## F-02: Hummingbot Integration

**Approach**: Use Hummingbot bot framework as trading layer

**Failed At**: Session 17 (estimated - not explicitly documented)

**Reason**: **Complexity overhead**

Hummingbot designed for professional trading firms:
- Extensive configuration (exchange connectors, strategies, risk parameters)
- Python framework (requires deep understanding to customize)
- Human-oriented dashboards (not AI-first interface)
- Over-engineered for Rhiz use case (simple DCA, small capital)

**Example Complexity**:
- Hummingbot config files: 10+ YAML files, 200+ parameters
- Strategy customization: Requires Python class inheritance, event handlers
- Learning curve: Weeks to understand architecture

**Rhiz Need**: Simple MCP tools for Kraken API (get balance, place order, get ticker)

**Pivot**: Fathom MCP (direct Kraken integration)

**Pivot Rationale**:
- AI-native interface (MCP protocol)
- Exactly what's needed (8 tools Phase 1, expand to 6 phases)
- No dashboard overhead (tools, not UI)
- Simple to understand (300 lines Python for Phase 1)

**Outcome**: ✅ Success
- Fathom Phase 1 deployed (Session 16)
- First trade validated (100% pipeline success)
- Hummingbot API still running on VPS (parallel infrastructure, not deprecated)

**Learning**: Build exactly what's needed, not what's comprehensive. Complexity should match immediate need.

**Note**: Hummingbot not deleted - kept as alternative approach if Fathom limitations discovered. Parallel infrastructure = options.

See: `docs/architecture/trading_pipeline_first_trade_case_study.md`

---

## F-03: Cloudflare Argo Tunnel

**Approach**: Use Cloudflare Argo Tunnel for VPS → Cloudflare routing

**Failed At**: Session 6 (Jan 3, 2026)

**Reason**: Tunnel not configured properly

**Problem**: DNS CNAME record pointing to `273e5f2d-af6c-446c-bc75-238b34c6c772.cfargotunnel.com`, but:
- No `.cloudflared/config.yml` file on VPS
- Tunnel daemon not running
- Result: 502 Bad Gateway errors

**Symptoms**:
```bash
$ curl https://fathom.dreamthewilderness.com/
# 502 Bad Gateway (Cloudflare error page)
```

**Diagnosis**: Argo Tunnel requires:
1. `cloudflared` daemon running on VPS
2. Configuration file mapping tunnel → services
3. Tunnel authentication

**None of these existed** on VPS.

**Pivot**: Direct A record to VPS IP

**Pivot Rationale**:
- Simpler (no tunnel daemon, no config file)
- Functional immediately
- Traefik handles SSL termination + reverse proxy (already configured)
- Cloudflare proxy still active (DDoS protection, CDN)

**Implementation**:
1. Deleted CNAME record
2. Created A record: `fathom.dreamthewilderness.com` → `72.62.81.128` (proxied)
3. Verified: https://fathom.dreamthewilderness.com/ operational

**Outcome**: ✅ Success
- Direct routing functional (Session 6+)
- SSL working (Cloudflare termination)
- Traefik routing correctly

**Learning**: Simple solution that works > complex solution that doesn't. Argo Tunnel adds value for multiple origins or advanced routing; not needed for single VPS.

See: `docs/knowledge_base/deployments/vps_topology.md`

---

## F-04: Traefik TLS-ALPN-01 Challenge

**Approach**: Use Traefik TLS-ALPN-01 challenge for Let's Encrypt SSL certificate

**Failed At**: Session 6 (Jan 3, 2026)

**Reason**: Cloudflare proxy blocks ALPN negotiation

**Problem**: Traefik attempting TLS-ALPN-01 challenge:
```yaml
labels:
  - "traefik.http.routers.fathom.tls.certresolver=mytlschallenge"
```

**Result**: Let's Encrypt rate limited (5 failed attempts)

**Diagnosis**:
- TLS-ALPN-01 requires direct TLS negotiation (no proxy)
- Cloudflare proxy intercepts TLS traffic (terminates at Cloudflare edge)
- Let's Encrypt cannot reach VPS directly for ALPN challenge

**Pivot**: Cloudflare SSL termination (Flexible mode)

**Pivot Rationale**:
- Cloudflare already handles SSL (client → Cloudflare HTTPS)
- VPS doesn't need its own SSL cert (Cloudflare → VPS HTTP trusted)
- Simpler (no Let's Encrypt challenge)

**Implementation**:
1. Removed TLS certresolver from Traefik labels
2. Set Cloudflare SSL mode: Flexible (Cloudflare → origin HTTP)
3. Verified: https://fathom.dreamthewilderness.com/ HTTPS (Cloudflare cert)

**Outcome**: ✅ Success
- SSL functional (Cloudflare termination)
- No Let's Encrypt complexity
- Traefik handles HTTP routing only

**Learning**: When using Cloudflare proxy, let Cloudflare handle SSL. Don't fight proxy behavior.

**Alternative Considered**: HTTP-01 challenge (requires port 80 open, Cloudflare proxy off)
- **Rejected**: Disabling proxy loses DDoS protection, CDN
- **Why**: Flexible SSL simpler, functional

See: `docs/knowledge_base/deployments/vps_topology.md`

---

## F-05: Threshold 0.45 for Skills

**Approach**: Use threshold 0.45 for semantic skill routing (inherited from checkpoint search)

**Failed At**: Session 71 (Jan 24, 2026)

**Reason**: **Multi-component embedding signal dilution**

**Problem**: Skill routing accuracy 56.7% (17/30 test cases) at threshold 0.45

**Root Cause Discovery**:
- Skill fingerprints = description + utterances + category + tools (multi-component)
- Checkpoint search = single narrative text (single-component)
- Multi-component embeddings dilute signal across semantic components
- Genuine skill matches scoring 0.25-0.70 vs checkpoint matches 0.40-1.0

**Why 0.45 Worked for Checkpoints**:
- Checkpoint text: cohesive narrative
- Embedding: single semantic unit
- High-quality matches: 0.40-1.0 range
- Threshold 0.45 filters noise, preserves signal

**Why 0.45 Failed for Skills**:
- Skill fingerprint: fragmented across components
- Embedding: diluted signal
- High-quality matches: 0.25-0.70 range (lower due to dilution)
- Threshold 0.45 rejected genuine matches (false negatives)

**Pivot**: Threshold 0.25 for skills

**Pivot Rationale**:
- Empirical testing showed clear matches at 0.25-0.70
- Noise still below 0.20
- Threshold 0.25 compensates for signal dilution

**Outcome**: ✅ Success (93.3% accuracy)
- Accuracy jumped 56.7% → 93.3%
- False positives: 0
- All domain categories 100% except ambiguous edge cases

**Learning**: Threshold must match vector topology. Multi-component embeddings require lower thresholds than single-text.

**Topology-Aware Thresholds**:
- Skills (multi-component): 0.25
- Checkpoints (single-text): 0.45
- Meta-queries (sparse concepts): 0.15-0.20 (future)

See: `docs/research/semantic_routing_accuracy_optimization.md`

---

## F-06: LLM-Based Self-RAG

**Approach**: Use LLM to decide whether to retrieve memory context (true Self-RAG paper approach)

**Failed At**: Session 72 (Jan 24, 2026)

**Reason**: **2-5 seconds latency unacceptable**

**Self-RAG Paper Approach**:
```python
def should_retrieve(query: str) -> bool:
    # Use LLM to decide
    prompt = f"Should we retrieve context for: {query}"
    response = llm.generate(prompt)
    return "yes" in response.lower()
```
- **Latency**: 2-5 seconds (LLM inference)
- **Accuracy**: High (LLM understands nuance)

**Problem**: 2-5s per retrieval decision = session start delays
- 3 skills × 2s decision = 6s overhead (unacceptable for session start)

**Pivot**: Heuristic Self-RAG

**Pivot Rationale**:
- Skill-specific defaults (trading always retrieves, execution never)
- Complexity keywords (analyze, compare, historical → retrieve)
- Query length heuristic (>15 words → retrieve)

**Implementation**:
```python
def should_retrieve_memory(skill_name: str, query: str) -> bool:
    # Skill-specific defaults
    if skill_name.startswith("trading/"):
        return True  # <1ms

    # Complexity heuristics
    if len(query.split()) > 15:
        return True  # <1ms

    complexity_keywords = ["analyze", "compare", "historical"]
    if any(kw in query.lower() for kw in complexity_keywords):
        return True  # <1ms

    return False
```

**Outcome**: ✅ Success
- Decision time: <5ms (vs 2-5s for LLM)
- Accuracy: 100% (5/5 test cases)
- Session start overhead: <15ms total (3 skills × 5ms)

**Learning**: **YAGNI** (You Ain't Gonna Need It) for LLM complexity. Simple heuristics often sufficient.

**When to Use LLM vs Heuristics**:
- **LLM**: Complex, nuanced decisions (e.g., strategy selection, regime classification)
- **Heuristics**: Binary decisions with clear patterns (e.g., should retrieve, is complex query)

See: `docs/research/semantic_routing_accuracy_optimization.md`

---

## F-07: Utterance Expansion Only

**Approach**: Improve skill routing accuracy solely by expanding utterance count

**Failed At**: Session 71 (Jan 24, 2026)

**Reason**: **Diminishing returns** - coverage not the bottleneck

**Hypothesis**: Low accuracy (56.7%) due to insufficient training examples

**Test**: Expanded utterances 45 → 97 (+52 new)

**Result**: Accuracy improved 56.7% → 70% (+13.3 percentage points)

**Diagnosis**: Improvement but not sufficient (target: 90%+)

**Root Cause**: Threshold was bottleneck, not coverage
- Genuine matches scoring 0.25-0.40 (below threshold 0.45)
- More utterances didn't change score distribution
- Threshold adjustment needed

**Pivot**: Threshold tuning (0.45 → 0.25)

**Pivot Rationale**:
- Utterance expansion showed diminishing returns
- Score distribution analysis revealed signal dilution
- Threshold adjustment addresses root cause

**Outcome**: ✅ Success (93.3% accuracy)
- Threshold 0.25 + 97 utterances = 93.3%
- Both coverage (utterances) and threshold needed

**Learning**: Test hypotheses incrementally. Utterance expansion taught us threshold was real issue.

**Pattern**: First attempt often reveals deeper problem. Partial success = keep digging.

See: `docs/research/semantic_routing_accuracy_optimization.md`

---

## F-08: LocalAI Deployment

**Approach**: Deploy LocalAI for local LLM inference

**Failed At**: Deferred (not attempted)

**Reason**: **Not blocking for current operations** + Ollama simpler

**Context**: Session 1 architectural framework mentioned LocalAI for local inference

**Decision**: Deferred in favor of Ollama

**Why Deferred**:
1. **Not blocking**: Trading operations don't require local LLM (Fathom uses Kraken API, not LLM)
2. **Complexity**: LocalAI requires configuration, model downloads, resource allocation
3. **Alternative exists**: Ollama simpler (single binary, easy model management)
4. **Resource constrained**: Dell Inspiron 16GB RAM (LocalAI + models = 8GB+)

**Pivot**: Ollama (when local LLM needed for Mem0)

**Pivot Rationale**:
- Simpler deployment (download + run)
- Easier model management (`ollama pull qwen2.5-coder:7b`)
- Lower resource overhead
- Active development, good docs

**Outcome**: ✅ Success
- Ollama deployed (Session 72)
- qwen2.5-coder:7b running for Mem0 backend
- Performance acceptable (10-20 tokens/sec CPU-only)

**Learning**: Defer non-blocking work. LocalAI may be revisited if Ollama limitations discovered, but so far Ollama sufficient.

**Status**: LocalAI remains in `external/` directory (reference implementation, not deployed)

---

## Failure Patterns Observed

### Pattern 1: Pivot Over Persist

**Observation**: When approach fails, pivot quickly vs persist indefinitely

**Examples**:
- JSON → YAML (Session 1, immediate pivot)
- Hummingbot → Fathom MCP (Session 17, clean pivot)
- Argo Tunnel → Direct A record (Session 6, 15 min pivot)
- LLM Self-RAG → Heuristic Self-RAG (Session 72, same-session pivot)

**Anti-Pattern**: Sunk cost fallacy (persist because already invested time)

**Learning**: Recognize failure early, pivot decisively. Time invested ≠ reason to continue.

### Pattern 2: Empirical Testing Reveals Root Cause

**Observation**: First hypothesis often wrong, testing reveals deeper issue

**Examples**:
- Thought: Utterance coverage issue → Reality: Threshold issue
- Thought: Argo Tunnel misconfigured → Reality: Don't need tunnel
- Thought: LocalAI needed → Reality: Ollama simpler

**Learning**: Test incrementally, observe results, update hypothesis. First explanation rarely complete.

### Pattern 3: Complexity Red Flag

**Observation**: High complexity often indicates wrong approach

**Examples**:
- Hummingbot (10+ config files) → Fathom (8 simple tools)
- JSON escaping narratives → YAML multi-line natural
- LLM Self-RAG (2-5s latency) → Heuristic (<5ms)

**Learning**: If approach feels overly complex, probably wrong tool for job. Simple solutions often correct.

### Pattern 4: Failures Preserved, Not Hidden

**Observation**: All failures documented in checkpoints + this genealogy

**Why**:
1. **Training data**: Future model instances learn from failures
2. **Pattern recognition**: Repeated failures reveal systemic issues
3. **Decision context**: Understanding why X rejected informs future choices

**Anti-Pattern**: Delete failure artifacts, pretend they didn't happen

**Learning**: Failure documentation as valuable as success documentation.

---

## Cross-References

**Checkpoints**:
- Every checkpoint has `alternatives_rejected` section documenting failures
- Session 1: JSON vs YAML decision
- Session 6: Argo Tunnel, Traefik TLS failures
- Session 72: Threshold tuning, Self-RAG failures

**Architecture Documents**:
- `docs/knowledge_base/decisions/architecture_decisions.md` - Successful pivots documented
- `docs/research/semantic_routing_accuracy_optimization.md` - Threshold tuning journey (failures → breakthrough)

**Session Syntheses**:
- `docs/sessions/session_73_architectural_synthesis.md` - 85/0 pattern as failure of integration planning

---

**End of Failure Genealogy**

*Last Updated: 2026-01-25 (Session 74)*
*Total Failures: 8 documented (all led to successful pivots)*
*Pattern: Pivot decisively, test empirically, preserve learnings*
*Principle: "Failure is information" - document thoroughly*
