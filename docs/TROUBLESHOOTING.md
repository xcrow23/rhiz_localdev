# Rhiz Troubleshooting Guide

**Purpose**: Document known issues, symptoms, diagnoses, and solutions
**Last Updated**: 2026-01-25 (Session 74)
**Coverage**: 40 days of operational experience (Dec 17, 2025 - Jan 25, 2026)

---

## Quick Index

| System | Common Issues | Sessions Affected |
|--------|---------------|-------------------|
| [Memory System](#memory-system) | Qdrant connection, quality degradation, embedding errors | Sessions 3, 22, 40 |
| [Skills Routing](#skills-routing) | Threshold tuning, signal dilution, utterance coverage | Sessions 71-72 |
| [Trading Pipeline](#trading-pipeline) | Paper mode, approval workflow, integration gaps | Sessions 6, 16, 42 |
| [Infrastructure](#infrastructure) | Traefik networking, Cloudflare DNS, Docker limits | Sessions 6, 40 |
| [Windows Compatibility](#windows-compatibility) | Emoji encoding, console output, path separators | Session 22 |

---

## Memory System

### Issue 1: Qdrant Connection Failed

**Symptom**: `ConnectionError: Cannot reach Qdrant at localhost:6333`

**Diagnosis**: Qdrant Docker container not running or port not exposed

**Solution**:
```bash
# Check if Qdrant container is running
docker ps | grep qdrant

# If not running, start it
cd infrastructure/docker
docker-compose up -d qdrant

# Verify port is exposed
curl http://localhost:6333/health
# Should return: {"status":"ok"}
```

**Prevention**: Add Qdrant health check to session_start hook

**Session Reference**: Session 3 (Dec 23, 2025) - Initial memory system deployment

---

### Issue 2: Embedding Dimension Mismatch

**Symptom**: `ValueError: Expected embedding dimension 384, got 768`

**Diagnosis**: Using wrong embedding model (all-MiniLM-L6-v2 = 384-dim, bert-base = 768-dim)

**Root Cause**: Model configuration mismatch between ingestion and search

**Solution**:
```python
# Verify current model
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
print(model.get_sentence_embedding_dimension())  # Should be 384

# If wrong model, re-ingest all checkpoints with correct model
python core/memory/ingest_checkpoints.py --model all-MiniLM-L6-v2
```

**Prevention**: Document embedding model in Qdrant collection metadata

**Configuration File**: `tools/memory-mcp/config.py`
```python
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # NEVER CHANGE (breaks existing vectors)
EMBEDDING_DIM = 384
```

---

### Issue 3: Memory Quality Degradation

**Symptom**: Memory search returns increasingly irrelevant results over time

**Diagnosis**: Checkpoint quality score degraded (Session 22: 0.73 → 0.14 without detection)

**Root Cause**: No automated quality monitoring, schema validation insufficient

**Solution**:
```bash
# Run checkpoint validation tool
python core/memory/checkpoint_validator.py

# Check quality scores
python core/memory/checkpoint_validator.py --report
# Look for scores <0.5 (poor quality threshold)

# For degraded checkpoints, manual review and enhancement
```

**Prevention**: Automated quality scoring in session_end hook (implemented Session 22)

**Quality Metrics** (7-point assessment):
1. Schema compliance (required fields present)
2. Session arc completeness (objective, narrative, outcomes)
3. Decisions documented (with rationale)
4. Working memory coherence (mental models, hypotheses)
5. Alternatives rejected (what didn't work, why)
6. Cross-references (related sessions, checkpoints)
7. Suggested resume prompt (clear next steps)

**Target Score**: >0.7 for excellent session continuity

**Session Reference**: Session 22 (Jan 22, 2026) - Quality degradation detected and resolved

---

### Issue 4: Qdrant Out of Memory

**Symptom**: Qdrant container crashes with `OOMKilled`

**Diagnosis**: Docker memory limit exceeded (default 2GB for Qdrant)

**Root Cause**: Large vector collections + in-memory storage

**Solution**:
```yaml
# Update docker-compose.yml
services:
  qdrant:
    image: qdrant/qdrant:latest
    mem_limit: 4g  # Increase from 2g
    environment:
      - QDRANT__STORAGE__ON_DISK_PAYLOAD=true  # Store payload on disk
    volumes:
      - ./qdrant_storage:/qdrant/storage
```

**Prevention**: Use on-disk storage mode for large collections (>1000 vectors)

**Monitoring**: Check Qdrant metrics at http://localhost:6333/metrics

---

### Issue 5: Vector Search Returns Nothing

**Symptom**: `memory_search("query")` returns empty list despite relevant content existing

**Diagnosis**: Threshold too high for query type (sparse concepts need lower threshold)

**Root Cause**: Using fixed threshold (0.45) for all query types

**Solution** (topology-aware thresholds):
```python
# Adjust threshold based on query type
memory_search("dyadic partnership", threshold=0.45)  # Relational (dense clusters)
memory_search("VPS deployment", threshold=0.30)     # Operational (medium spread)
memory_search("what did we learn", threshold=0.20)  # Meta-cognitive (sparse concepts)
```

**Threshold Recommendations** (from Session 72 threshold tuning):
- Relational concepts: 0.45+ (tight clustering, 0.50-0.60 similarity)
- Operational queries: 0.25-0.40 (medium spread, 0.30-0.50 similarity)
- Meta-cognitive queries: 0.15-0.20 (sparse concepts, 0.15-0.30 similarity)

**Session Reference**: Session 72 (Jan 24, 2026) - Threshold tuning breakthrough

---

## Skills Routing

### Issue 6: Low Routing Accuracy (<85%)

**Symptom**: Skill routing test shows <85% accuracy (below target)

**Diagnosis**: Threshold too high or utterance coverage insufficient

**Historical Journey**:
- Session 71: 56.7% accuracy (threshold 0.45, 45 utterances)
- Session 71 (utterance expansion): 70% accuracy (threshold 0.45, 97 utterances)
- Session 72 (threshold tuning): 93.3% accuracy (threshold 0.25, 97 utterances)

**Root Cause Discovery**: Multi-component embedding signal dilution
- Skill fingerprints combine: description + utterances (97 items) + category + tools
- Signal dilutes across components
- Single-text embeddings: 0.40-1.0 similarity range (high contrast)
- Multi-component embeddings: 0.25-0.70 similarity range (dilution)

**Solution**:
```python
# Lower threshold to compensate for multi-component dilution
# File: core/skills/router.py
ROUTING_THRESHOLD = 0.25  # Down from 0.45
```

**Verification**:
```bash
# Run routing accuracy test
python core/skills/test_routing_accuracy.py
# Target: >85% (currently 93.3%)
```

**Session Reference**: Sessions 71-72 (Jan 24, 2026) - Threshold tuning journey

---

### Issue 7: Skill Routes to Wrong Domain

**Symptom**: Query "analyze BTC price" routes to infrastructure/troubleshooting instead of trading/kraken_analysis

**Diagnosis**: Utterance coverage gap for that specific query pattern

**Solution**:
```yaml
# Add utterance to correct skill
# File: core/skills/registry/trading_kraken_analysis.yaml
utterances:
  - analyze BTC price
  - analyze bitcoin price
  - analyze market conditions
  - what's the price doing
  # ... existing utterances
```

**Verification**: Re-run routing test after utterance addition

**Note**: Don't over-expand utterances (diminishing returns after ~100). Threshold tuning more effective.

---

### Issue 8: Skills Activate But Don't Execute

**Symptom**: Skill routes correctly (93.3% accuracy), loads Mem0 context, but doesn't invoke MCP tools

**Diagnosis**: **EXPECTED BEHAVIOR** - Skill-tool binding framework not yet implemented

**Status**: Known gap (85/0 pattern), Phase 2 work

**Current Workflow**:
1. ✅ Query → Semantic routing (93.3% accurate)
2. ✅ Skill activation → Loads context from Mem0
3. ❌ Tool invocation → **MISSING** (no binding framework)

**Planned Resolution**: Phase 2 skill-tool binding framework (3-5 hours estimated)

**Session Reference**: Session 42 (Jan 10, 2026) - Integration gaps identified

---

### Issue 9: Mem0 Memory Loading Slow (>2s)

**Symptom**: Session startup takes 2-3 seconds for skill context loading

**Diagnosis**: Ollama CPU-only inference (10-20 tokens/sec on AMD Ryzen 5 7530U)

**Root Cause**: No GPU acceleration, qwen2.5-coder:7b model on CPU

**Solution Options**:
1. **Accept current performance** (<3s session startup acceptable)
2. **Upgrade hardware** (add GPU: AMD RX 6600 or NVIDIA RTX 3060, ~$200-300)
3. **Use lighter model** (qwen2.5-coder:3b, faster but lower quality)
4. **Cloud inference** (Anthropic API for Mem0, ~$0.01/session)

**Current Decision**: Accept current performance (non-blocking for session start)

**Future Enhancement**: GPU upgrade when budget allows (10x speedup: 100+ tokens/sec)

**Session Reference**: Session 72 (Jan 24, 2026) - Mem0 integration complete

---

## Trading Pipeline

### Issue 10: Paper Mode Enforcement Needed

**Symptom**: Live trading discovered on VPS during infrastructure reconnaissance (Session 6)

**Diagnosis**: Critical safety gap - production trading active without Captain awareness

**Immediate Response**: Enforced paper mode immediately (safety-first pattern)

**Solution Applied**:
```python
# File: domains/trading/fathom_commander/config.py
PAPER_MODE = True  # NEVER set to False without Captain explicit approval
LIVE_TRADING_ALLOWED = False
```

**Verification**:
```bash
# Check current mode
curl http://95.217.51.24:8000/api/trading/mode
# Should return: {"mode": "paper", "live_trading": false}
```

**Safety Protocol**:
1. Detect unsafe state (live trading without approval)
2. Enforce immediately (paper mode)
3. Document (checkpoint + handoff)
4. Captain confirmation before live mode re-enabled

**Session Reference**: Session 6 (Jan 3, 2026) - Infrastructure discovery & safety intervention

---

### Issue 11: First Trade Execution (Validation)

**Symptom**: No issues - 100% pipeline validation on first attempt!

**Details**:
- Date: Dec 26, 2025 (Session 16)
- Trade: 0.0001 BTC @ $87,420
- TXID: OBRP7D-MBTUR-4R2O6T
- Cost: $8.74 + $0.03 fee
- Execution Time: <10 seconds
- Pipeline: Pre-flight validation → Memory-first logging → Order placement → Fill confirmation

**Why It Worked**:
- Safety architecture already built (MAX_ORDER_USD, approval thresholds)
- Dyadic approval pattern established (Captain: "Execute it!" - no hesitation)
- All three subsystems coordinated (Fathom + FC + SIL)
- Memory-first logging (decision recorded before execution)

**Key Learning**: Extensive preparation enables confident execution when stakes are real

**Session Reference**: Session 16 (Dec 26, 2025) - First trade case study

---

### Issue 12: Trading Integration Workflow Missing

**Symptom**: Cannot execute intelligent trades despite having Fathom (Phase 1), FC (27 tools), and SIL (B+ grade)

**Diagnosis**: **EXPECTED BEHAVIOR** - 85/0 pattern (components exist, workflows missing)

**Status**: Known gap, Phase 2 work

**Missing Integration**:
```
Market Data (Fathom Phase 1)
  ↓ [MISSING WORKFLOW]
Intelligence (SIL Decision Engine)
  ↓ [MISSING WORKFLOW]
Orchestration (Fathom Commander)
  ↓ [FATHOM PHASE 2 MISSING]
Execution (Fathom Phase 2-6, pending)
```

**Blockers**:
1. FC HTTP Gateway not deployed (requires Captain VPS access)
2. Fathom Phase 2-6 not implemented (trading operations)
3. Integration workflow not designed

**Planned Resolution**: Phase 2 Component Integration (Session 75-76+, 15-25 hours estimated)

**Session Reference**: Session 42 (Jan 10, 2026) - 85/0 pattern discovered

---

### Issue 13: Kraken API Rate Limiting

**Symptom**: `429 Too Many Requests` error from Kraken API

**Diagnosis**: Exceeded API rate limits (varies by tier and endpoint)

**Kraken Rate Limits** (free tier):
- Public endpoints: 1 request/second
- Private endpoints: 15 requests/minute (counter decay)
- Burst: Short bursts allowed, counter increases by cost

**Solution**:
```python
# Implement rate limiting in Fathom
# File: domains/trading/fathom/rate_limiter.py
import time
from functools import wraps

def rate_limit(calls_per_second=1):
    min_interval = 1.0 / calls_per_second
    last_called = [0.0]

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            wait_time = min_interval - elapsed
            if wait_time > 0:
                time.sleep(wait_time)
            result = func(*args, **kwargs)
            last_called[0] = time.time()
            return result
        return wrapper
    return decorator

@rate_limit(calls_per_second=1)
def get_ticker(pair):
    # Kraken API call
    ...
```

**Prevention**: Cache frequently accessed data (ticker, orderbook), use websockets (Phase 3)

---

## Infrastructure

### Issue 14: Traefik Networking (Dual Networks Required)

**Symptom**: n8n webhooks timeout, FC HTTP calls fail, services can't communicate

**Diagnosis**: Traefik routing misconfigured - needs both external and internal networks

**Root Cause**: Default Docker Compose creates single network, Traefik needs both for routing

**Solution**:
```yaml
# docker-compose.yml
version: '3.8'

networks:
  traefik_public:
    external: true  # Created manually: docker network create traefik_public
  internal:
    driver: bridge

services:
  traefik:
    networks:
      - traefik_public
      - internal
    labels:
      - "traefik.http.routers.traefik.entrypoints=websecure"
      - "traefik.http.routers.traefik.rule=Host(`traefik.example.com`)"

  fathom_commander:
    networks:
      - traefik_public
      - internal
    labels:
      - "traefik.http.routers.fc.entrypoints=websecure"
      - "traefik.http.routers.fc.rule=Host(`fc.example.com`)"
```

**Verification**:
```bash
# Test internal routing
docker exec n8n curl http://fathom_commander:8000/health
# Should return: {"status":"ok"}

# Test external routing (via Traefik)
curl https://fc.example.com/health
# Should return: {"status":"ok"}
```

**Session Reference**: Session 6 (Jan 3, 2026) - Traefik debugging (45 min)

---

### Issue 15: Cloudflare DNS Not Resolving

**Symptom**: `fathom.dreamthewilderness.com` returns 502 Bad Gateway

**Diagnosis**: DNS CNAME pointed to Argo Tunnel that didn't exist

**Original Config** (broken):
- CNAME: `273e5f2d-af6c-446c-bc75-238b34c6c772.cfargotunnel.com`
- No `cloudflared` daemon running on VPS
- No tunnel configuration file

**Solution**: Switch to direct A record
```
Type: A
Name: fathom
Content: 72.62.81.128
Proxy: Enabled (orange cloud)
TTL: Auto
```

**Why This Works**:
- Cloudflare proxy provides DDoS protection + CDN
- Traefik handles SSL termination on VPS (Cloudflare Flexible SSL mode)
- No tunnel complexity needed for single VPS

**Session Reference**: Session 6 (Jan 3, 2026) - Infrastructure fixes

---

### Issue 16: Docker Resource Limits Not Set

**Symptom**: Docker Desktop consuming excessive RAM/CPU, slowing Windows

**Diagnosis**: No explicit resource limits configured

**Solution**:
```yaml
# docker-compose.yml - Add resource limits
services:
  qdrant:
    mem_limit: 2g
    mem_reservation: 1g
    cpus: 2

  ollama:
    mem_limit: 4g  # Model loading requires more RAM
    mem_reservation: 2g
    cpus: 4
```

**Docker Desktop Settings** (Windows):
1. Open Docker Desktop → Settings → Resources
2. Set Memory: 12GB (out of 16GB total)
3. Set CPUs: 4 (out of 6 cores available)
4. Set Swap: 2GB
5. Apply & Restart

**Monitoring**:
```bash
# Check resource usage
docker stats

# Look for containers near limits
docker stats --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"
```

---

### Issue 17: VPS IP Confusion (72.62.81.128 vs 95.217.51.24)

**Symptom**: Documentation references two different IPs, unclear if migration or separate services

**Diagnosis**: **UNRESOLVED** - requires Captain confirmation

**Current Understanding**:
- **72.62.81.128**: Hostinger VPS (production infrastructure, 9 containers)
- **95.217.51.24**: Hetzner VPS (FastAPI Gateway for testing?)

**Questions for Captain**:
1. Are these the same VPS after migration?
2. Two separate VPS deployments (Hostinger + Hetzner)?
3. Which IP should be canonical in documentation?

**Workaround**: Document both IPs with "[CAPTAIN CONFIRMATION NEEDED]" note

**Session Reference**: Session 73 (Jan 25, 2026) - VPS identity confusion flagged

---

## Windows Compatibility

### Issue 18: Emoji Encoding Crashes Console

**Symptom**: `UnicodeEncodeError: 'charmap' codec can't encode character '\u2705'`

**Diagnosis**: Windows console uses 'charmap' codec, can't display Unicode emoji

**Root Cause**: Windows platform constraint (Linux/Mac use UTF-8 by default)

**Solution**: Replace emoji with ASCII-safe alternatives
```python
# Before (broken on Windows)
print("✅ Success")
print("❌ Failed")
print("⚠️ Warning")

# After (Windows-safe)
print("[OK] Success")
print("[FAIL] Failed")
print("[WARN] Warning")
```

**Configuration**:
```python
# File: core/utils/platform.py
import sys

IS_WINDOWS = sys.platform == 'win32'

def safe_output(text, emoji=None, ascii_fallback=None):
    if IS_WINDOWS and emoji:
        return f"{ascii_fallback} {text}"
    elif emoji:
        return f"{emoji} {text}"
    return text

# Usage
print(safe_output("Success", emoji="✅", ascii_fallback="[OK]"))
```

**Session Reference**: Session 22 (Jan 22, 2026) - Windows encoding fixes

---

### Issue 19: Path Separator Issues

**Symptom**: File paths break on Windows (`core/memory/checkpoints/file.yaml` vs `core\memory\checkpoints\file.yaml`)

**Diagnosis**: Hardcoded forward slashes don't work on Windows

**Solution**: Use `pathlib` or `os.path.join`
```python
# Before (broken on Windows)
checkpoint_path = "core/memory/checkpoints/session_74.yaml"

# After (cross-platform)
from pathlib import Path

checkpoint_path = Path("core") / "memory" / "checkpoints" / "session_74.yaml"
# Or
import os
checkpoint_path = os.path.join("core", "memory", "checkpoints", "session_74.yaml")
```

**Best Practice**: Always use `pathlib.Path` for file operations (Python 3.4+)

---

## Orchestration

### Issue 20: n8n → Cloudflare Workers Migration Incomplete

**Symptom**: Mooncheck migrated successfully, but 9 trading workflows still on n8n

**Diagnosis**: **EXPECTED BEHAVIOR** - Migration prioritized mooncheck first (proof of concept)

**Status**: Known gap (85/0 pattern), Phase 2 work

**Current State**:
- ✅ Mooncheck: Migrated to Cloudflare Workers (70 lines TypeScript vs 2,847 lines JSON)
- ❌ Trading workflows: Still on n8n (9 workflows, ~33 hours migration effort)

**Blocker**: FC HTTP Gateway deployment (same as trading integration)

**Migration Priority** (for Phase 2):
1. Daily Health Monitor (simple, validates pattern)
2. Weekly DCA Buyer (validates trading workflow)
3. Smart DCA (more complex logic)
4. Portfolio Rebalancer
5. Daily Performance Journal
6. Weekly Strategy Review
7. Risk Monitor (complex, high effort)
8. Volatility Sentinel (complex)
9. Spread Scanner (low usage priority)

**Session Reference**: Session 40 (Jan 11, 2026) - Mooncheck migration complete

---

### Issue 21: Token Verification Not Implemented (Checkpoint API)

**Symptom**: checkpoint-api deployed to Cloudflare Workers, but token auth not validated on VPS endpoint

**Diagnosis**: VPS FastAPI Gateway doesn't verify token (security gap)

**Impact**: LOW (checkpoint writes currently via filesystem, not HTTP)

**Solution**:
```python
# File: infrastructure/vps/fastapi_gateway/main.py
from fastapi import Header, HTTPException
import os

@app.post("/checkpoints/write")
async def checkpoint_write(
    checkpoint_data: dict,
    authorization: str = Header(None)
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Missing token")

    token = authorization.split(" ")[1]
    if token != os.getenv("CHECKPOINT_TOKEN"):
        raise HTTPException(403, "Invalid token")

    # Proceed with checkpoint write
    ...
```

**Estimated Fix**: 1 hour (implementation + testing)

**Session Reference**: Session 40 (Jan 11, 2026) - Token verification flagged

---

## Debugging Techniques

### Memory System Debugging

```bash
# Check Qdrant collections
curl http://localhost:6333/collections

# Get collection info
curl http://localhost:6333/collections/rhiz_memories

# Search directly (bypass MCP)
curl -X POST http://localhost:6333/collections/rhiz_memories/points/search \
  -H "Content-Type: application/json" \
  -d '{
    "vector": [...],  # 384-dim embedding
    "limit": 5,
    "with_payload": true
  }'

# Validate checkpoints
python core/memory/checkpoint_validator.py --verbose
```

---

### Skills Routing Debugging

```bash
# Test routing accuracy
python core/skills/test_routing_accuracy.py --verbose

# Check skill fingerprint embeddings
python -c "
from core.skills.router import SkillRouter
router = SkillRouter()
router.load_skills()
for skill in router.skills:
    print(f'{skill.name}: {len(skill.utterances)} utterances')
"

# Test specific query
python -c "
from core.skills.router import SkillRouter
router = SkillRouter()
result = router.route('analyze BTC price')
print(f'Routed to: {result.skill_name} (score: {result.score})')
"
```

---

### Trading Pipeline Debugging

```bash
# Check Fathom health
curl http://localhost:8000/health  # Local
curl https://fathom.dreamthewilderness.com/health  # VPS

# Check FC status
curl http://95.217.51.24:8000/api/health

# Verify paper mode
curl http://95.217.51.24:8000/api/trading/mode
# Should return: {"mode": "paper"}

# Check trading rules
curl http://95.217.51.24:8000/api/trading/rules
# Returns: MAX_ORDER_USD, DAILY_TRADE_LIMIT, etc.
```

---

### Infrastructure Debugging

```bash
# Check Docker containers
docker ps  # Running containers
docker ps -a  # All containers (including stopped)

# Check container logs
docker logs fathom_commander --tail 50
docker logs traefik --tail 50

# Check Traefik routing
curl http://localhost:8080/api/http/routers  # Traefik dashboard API

# Check Cloudflare DNS
dig fathom.dreamthewilderness.com
nslookup fathom.dreamthewilderness.com
```

---

## Escalation Path

### When to Ask Captain

1. **Architecture decisions** (new integration approach, major refactoring)
2. **VPS access needed** (deployment, configuration changes)
3. **Real money involved** (trading execution, capital deployment)
4. **Safety concerns** (live trading detected, circuit breaker triggered)
5. **Uncertainty about direction** (multiple valid paths, strategic choices)
6. **Resource constraints** (hardware limitations, budget decisions)

### When to Search Memory First

1. **Technical issues** (likely documented in past checkpoints)
2. **Deployment procedures** (standardized, documented)
3. **Known patterns** (85/0 pattern, threshold tuning, etc.)
4. **Historical decisions** (why X was chosen over Y)

### When to Continue Autonomously

1. **Implementation work** (within granted scope)
2. **Bug fixes** (low-risk, non-destructive)
3. **Documentation updates** (accuracy improvements)
4. **Test execution** (validation, verification)
5. **Checkpoint writing** (session end)

---

## Related Resources

**Component Documentation**:
- Memory system: `docs/knowledge_base/components/memory_system.md`
- Skills system: `docs/knowledge_base/components/skills_system.md`
- Trading components: `docs/knowledge_base/components/fathom_*.md`

**Failure Documentation**:
- Failure genealogy: `docs/knowledge_base/decisions/failure_genealogy.md`
- Threshold tuning: `docs/knowledge_base/decisions/threshold_tuning.md`

**Session References**:
- Session 6 (Jan 3): Infrastructure discovery & safety
- Session 16 (Dec 26): First trade execution
- Session 22 (Jan 22): Quality degradation + Windows encoding
- Session 42 (Jan 10): Comprehensive audit, 85/0 pattern
- Sessions 71-72 (Jan 24): Threshold tuning breakthrough

---

**End of Troubleshooting Guide**

*Last Updated: 2026-01-25 (Session 74)*
*Coverage: 40 days operational experience*
*Next Update: After Phase 2 completion (new issues documented)*
