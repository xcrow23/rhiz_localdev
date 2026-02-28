# Test Suite Performance Analysis - Session 2
## Dell Inspiron 15 3535 (CPU-bound Hardware)

**Date:** January 24, 2026
**Hardware:** AMD Ryzen 5 7530U (6 cores, 12 threads), 16GB RAM, No GPU

---

## Executive Summary

**Current Performance Grade: C+**

- **Total Runtime:** ~3 minutes (180 seconds)
  - Unit tests: 77 seconds (24 tests)
  - Integration tests: 103 seconds (16 tests)
  - Accuracy tests: ~85 seconds (9 tests)
- **Test Count:** 49 tests total
- **Average per test:** ~3.7 seconds
- **Accuracy:** 56.7% (BELOW 85% target - requires investigation)

**Critical Finding:** Accuracy is significantly below target. This is a higher priority issue than runtime optimization.

---

## Detailed Timing Breakdown

### Router Initialization
- **First initialization:** ~7.5 seconds (session-scoped fixture)
- **Subsequent in same process:** ~7-9 seconds (new router instances)
- **Components:**
  - Model load (SentenceTransformer): ~5-6 seconds
  - Qdrant connection: ~500ms
  - Metadata load: <10ms (cached after first load)

### Query Performance
- **Per query embedding + search:** ~2 seconds
- **Target in router.py:** <3000ms (realistic for CPU-bound system)
- **Current performance:** Meeting target (2000-2100ms per query)

### Session-Scoped Fixtures
The `skill_router` fixture is session-scoped, which should amortize initialization cost:
- First test in session pays ~9.5s setup (model load + Qdrant check)
- Subsequent tests reuse same router instance
- However, many tests create NEW routers directly (bypassing fixture)

---

## Performance Bottlenecks

### 1. Model Loading (Highest Impact)
**Time:** 5-6 seconds per instance
**Frequency:** Once per session for fixture, but multiple times for direct instantiation
**Impact:** HIGH

**Breakdown:**
```python
# test_router.py line 47-50 - Connection failure test
with pytest.raises(RuntimeError):
    SkillRouter(qdrant_host="invalid-host", port=9999)  # NEW ROUTER: +6s
```

**Occurrences:**
- `test_initialization_qdrant_connection_failure`: NEW router (6s)
- `test_initialization_model_load_failure`: NEW router (5s)
- `test_route_query_collection_not_exist`: NEW router (9s)
- `test_error_handling_collection_missing`: NEW router (9s)

**Total wasted time:** ~30 seconds from redundant model loads

### 2. Qdrant Query Time
**Time:** 20-30ms per query (embedded in 2s total)
**Frequency:** Every `route_query()` call
**Impact:** MEDIUM

**Analysis:**
- Embedding generation: ~1.5-1.8s (CPU-bound, unavoidable)
- Qdrant vector search: ~20-30ms (acceptable)
- Overhead: ~100-200ms

### 3. Test Class Setup
**Time:** 6-23 seconds per test class
**Frequency:** Per test class (5 classes)
**Impact:** MEDIUM

**Sessions scoped fixture overhead:**
```
TestMCPRouteToSkill setup: 23.34s (imports MCP server module)
TestEndToEndRouting setup: 6.82s
```

### 4. Concurrent Test Execution
**Time:** 6.4 seconds for 25 concurrent queries
**Frequency:** One test
**Impact:** LOW (demonstrates scalability)

**Insight:** ThreadPoolExecutor with 10 workers handles 25 queries in 6.4s
- If serial: 25 × 2s = 50s
- Actual: 6.4s
- Speedup: ~7.8x (good parallelization)

---

## Scalability Projections

### Current State (6 skills)
- Qdrant collection size: 6 vectors
- Metadata file: 122 lines
- Query time: 2000ms
- Test suite: 49 tests, 180s

### Projected: 10 Skills
- Qdrant collection: 10 vectors (+67%)
- Metadata file: ~200 lines
- Query time: **2050ms** (+2.5%, vector search scales logarithmically)
- Test suite: ~70 tests, **240s** (linear scaling)

**Analysis:** Adding skills has MINIMAL impact on query performance (Qdrant uses HNSW index, logarithmic scaling).

### Projected: 20 Skills
- Qdrant collection: 20 vectors (+233%)
- Query time: **2100ms** (+5%)
- Test suite: ~100 tests, **350s**

**Analysis:** Still acceptable. Query time stays well under 3000ms target.

### Projected: 50 Skills
- Qdrant collection: 50 vectors (+733%)
- Query time: **2200ms** (+10%)
- Test suite: ~200 tests, **700s** (11-12 minutes)

**Analysis:**
- Query performance: Still acceptable (<3000ms)
- Test runtime: Becomes problematic without parallelization
- **Recommendation:** Introduce pytest-xdist at 30+ skills

---

## Resource Usage Analysis

### Memory Footprint
**Unable to measure** (psutil not installed in test environment)

**Estimated based on components:**
- SentenceTransformer model: ~500MB (all-MiniLM-L6-v2)
- Qdrant client: ~50MB
- Test fixtures: ~10MB
- **Total estimated:** ~600MB per pytest worker

**Constraint Check:**
- Available RAM: 16GB
- pytest-xdist with 4 workers: 4 × 600MB = 2.4GB
- **Verdict:** Memory is NOT a bottleneck for parallelization

### CPU Utilization
**Observed:** Model loading and embedding generation are CPU-intensive
- Model load: Likely using all 6 cores
- Query embedding: Single-threaded per query (transformers default)

**Parallelization Opportunity:**
- Current: Single pytest process, serial test execution
- With pytest-xdist (4 workers): 4× speedup potential
- **Estimated runtime with xdist:** 180s / 3.5 = ~50 seconds

---

## Accuracy Crisis (CRITICAL)

**Current Accuracy: 56.7%**
**Target Accuracy: 85%**
**Gap: -28.3 percentage points**

### Category Breakdown
| Category | Correct | Total | Accuracy |
|----------|---------|-------|----------|
| Trading | 4 | 8 | 50.0% |
| Memory | 3 | 8 | 37.5% ⚠️ |
| Infrastructure | 4 | 6 | 66.7% |
| Research | 3 | 4 | 75.0% |
| Edge Cases | 3 | 4 | 75.0% |

**Analysis:**
- Memory category is FAILING (37.5%)
- Trading category is borderline (50%)
- Only Research and Edge cases meet target

**Hypothesis for low accuracy:**
- Threshold 0.45 may be too conservative for multi-component embeddings
- Skill fingerprints may need richer utterance sets
- Alternative: Embeddings may need boosting (see route_with_context)

**This is a QUALITY issue, not a PERFORMANCE issue.**

---

## Optimization Opportunities

### 1. Mock Expensive Fixtures for Error Tests (HIGH IMPACT)
**Potential Savings:** ~30 seconds (16% of total runtime)

**Current:**
```python
def test_initialization_qdrant_connection_failure():
    with pytest.raises(RuntimeError):
        SkillRouter(qdrant_host="invalid-host", port=9999)  # Loads model: 6s
```

**Optimized:**
```python
@patch('core.skills.router.SentenceTransformer')
def test_initialization_qdrant_connection_failure(mock_transformer):
    mock_transformer.return_value = Mock()
    with pytest.raises(RuntimeError, match="Qdrant"):
        SkillRouter(qdrant_host="invalid-host", port=9999)  # ~100ms
```

**Tests to modify:**
- `test_initialization_qdrant_connection_failure`
- `test_route_query_collection_not_exist`
- `test_error_handling_collection_missing`

**Impact:** 30s → 0.3s for error path tests

### 2. pytest-xdist for Parallel Execution (MEDIUM IMPACT)
**Potential Savings:** 180s → ~50s (130s saved, 72% reduction)

**Implementation:**
```bash
pip install pytest-xdist
pytest -n 4  # 4 workers on 6-core CPU
```

**Caveat:** Session-scoped fixtures are tricky with xdist
- `skill_router` fixture would be created once PER WORKER
- 4 workers × 7.5s = 30s overhead
- Net benefit: (180s / 4) + 30s = 75s (still 58% improvement)

**Risk:** Qdrant connection pool exhaustion with many workers

### 3. Lazy Model Loading (LOW IMPACT)
**Potential Savings:** ~5 seconds (one-time)

**Current:** Model loads on SkillRouter.__init__()
**Proposed:** Load on first route_query() call

**Benefit:** Tests that instantiate router but don't query avoid model load
**Trade-off:** First query pays initialization cost (unexpected latency spike)

**Verdict:** NOT RECOMMENDED - violates principle of least surprise

### 4. Reduce Accuracy Test Query Count (LOW IMPACT)
**Potential Savings:** ~10-20 seconds

**Current:** 30 golden queries × 2s = 60s for main accuracy test
**Proposed:** Split into smoke test (5 queries) vs full validation (30 queries)

**Marker:**
```python
@pytest.mark.accuracy
@pytest.mark.slow
def test_golden_set_full_validation():
    # 30 queries
```

**Benefit:** CI can run smoke test (10s), full validation on-demand

---

## Hardware-Specific Considerations

### CPU-Bound Constraints
- No GPU acceleration for embeddings (expected 10-20× speedup with CUDA)
- CPU inference is inherently slow for transformer models
- Current performance is REALISTIC for this hardware

### Comparison to Production
**Production architecture** (per CLAUDE.md):
- Cloud infrastructure uses deterministic workflows, NOT semantic routing
- Skill routing is local development only
- VPS gateway uses FastAPI, not router

**Implication:** Production performance is irrelevant - optimize for developer experience

### Acceptable Performance Targets
Given CPU-bound hardware:
- Router init: <10s ✅ (currently 7.5s)
- Query time: <3000ms ✅ (currently 2000ms)
- Test suite: <5 minutes ⚠️ (currently 3 minutes, acceptable but borderline)

---

## Recommended Actions for Session 3

### Priority 1: Fix Accuracy (CRITICAL)
1. Investigate why accuracy is 56.7% vs target 85%
2. Options:
   - Lower threshold (0.40 instead of 0.45)
   - Add more utterances to skill fingerprints
   - Verify Qdrant ingestion correctness
3. Re-run ingest_skills.py with verbose logging
4. Check for embedding quality issues

**Time Estimate:** 30-45 minutes

### Priority 2: Mock Expensive Error Tests (HIGH VALUE)
1. Add `@patch` decorators to 4 error-path tests
2. Verify RuntimeError messages still validate correctly
3. Expected time savings: ~30 seconds

**Time Estimate:** 15 minutes
**Complexity:** Low

### Priority 3: Add Smoke Test Marker (MEDIUM VALUE)
1. Create `@pytest.mark.smoke` for quick validation
2. Move full golden test set to `@pytest.mark.accuracy` only
3. Update CI to run smoke tests by default

**Time Estimate:** 10 minutes

### Priority 4: Evaluate pytest-xdist (FUTURE)
**NOT recommended for Session 3** - session-scoped fixtures complicate xdist setup.

**Defer until:** 50+ skills or test suite >5 minutes

---

## Performance Monitoring Approach

### Metrics to Track
1. **Test runtime by category:**
   - Unit tests: <90s (currently 77s ✅)
   - Integration tests: <120s (currently 103s ✅)
   - Accuracy tests: <120s (currently 85s ✅)

2. **Router performance:**
   - Initialization: <10s
   - Query avg: <2500ms
   - Query p95: <3000ms

3. **Accuracy regression:**
   - Golden test set: >85% (currently 56.7% ❌)
   - Category minimums: >70% per category

### Monitoring Implementation
Add `pytest --durations=0` to CI:
```yaml
# .github/workflows/test.yml (future)
- name: Run tests with timing
  run: pytest --durations=0 --json-report
```

Store results in `docs/testing/performance_history.json`:
```json
{
  "2026-01-24": {
    "total_time": 180,
    "test_count": 49,
    "accuracy": 56.7,
    "hardware": "Dell Inspiron 15 3535"
  }
}
```

### Regression Alerts
Fail CI if:
- Total runtime >300s (5 minutes)
- Accuracy <85%
- Any single test >10s (indicates bottleneck)

---

## Scalability Verdict

### 10 Skills: ✅ ACCEPTABLE
- Runtime: ~240s (4 minutes)
- Query time: <2100ms
- No architectural changes needed

### 20 Skills: ✅ ACCEPTABLE WITH CAVEATS
- Runtime: ~350s (5.8 minutes)
- Query time: <2200ms
- **Recommend:** Add pytest-xdist to bring runtime to ~100s

### 50 Skills: ⚠️ OPTIMIZATION REQUIRED
- Runtime: ~700s (11.6 minutes) - unacceptable
- Query time: <2300ms (still acceptable)
- **Required:** pytest-xdist mandatory, consider test subsetting

---

## Conclusion

**Performance Grade: C+**

**Strengths:**
- Query performance meets CPU-bound hardware targets (<3000ms)
- Vector search scales well (Qdrant HNSW)
- Concurrent query handling works (7.8× speedup)
- Session-scoped fixtures partially amortize initialization cost

**Weaknesses:**
- Accuracy is CRITICALLY low (56.7% vs 85% target)
- Error path tests waste 30s on unnecessary model loads
- Test suite will hit 5-minute threshold at ~30 skills
- No memory leak testing or profiling implemented

**Immediate Action Required:**
1. **FIX ACCURACY** - this is blocking production use
2. Mock expensive fixtures in error tests
3. Add smoke test subset for fast validation

**Future Optimizations (defer to 30+ skills):**
- pytest-xdist for parallelization
- Test subsetting (smoke vs full)
- Performance regression tracking

---

**Next Session Focus:**
Session 3 must prioritize accuracy investigation over performance optimization.
A fast test suite that validates incorrect behavior is worse than a slow suite that catches real issues.
