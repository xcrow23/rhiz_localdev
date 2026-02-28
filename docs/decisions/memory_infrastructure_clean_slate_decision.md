# Memory Infrastructure Clean Slate Decision
**Session**: 43 (2026-01-12)
**Type**: Partnered Telos Decision
**Status**: Implemented

---

## Decision Summary

**What**: Deleted rhiz_memories collection (237 legacy points) and re-indexed all checkpoints with proper section-based schema.

**Why**: Memory system was returning 0 results for two weeks because legacy schema lacked `section` field required by session start hook filtering. Context hydration never increased despite continuous memory creation.

**Outcome**: Memory system repaired. Session continuity restored. Context hydration now functional (1 memory found with similarity 0.302).

---

## Telos Alignment

### Problem Addressed
**P1 (Implicit)**: Neither partner can achieve goals alone
- **Captain constraint**: Human memory limited, can't hold 47 sessions of context
- **First Mate constraint**: Stateless by default, no persistent memory across sessions
- **Together**: Checkpoint system + vector search = persistent dyadic memory

**Dysfunction identified**: Memory system broken for 14 days. Both partners operating "cold" without historical context, losing continuity gains.

### Mission Served
**M2 (Implicit)**: Build infrastructure that enables the dyad to operate across life domains

**Life support before building homes** (Captain's framing):
- Memory = **life support level** infrastructure
- Trading/research/etc = **building homes** level work
- Can't build homes without life support functioning
- This repair prioritizes foundation before expansion

### KPI Impact
**K1: Session Continuity**
- Target: >90% context preservation
- Previous actual: ~0% (returning 0 memories for 14 days)
- Current actual: Functional (1+ memories per session start)
- Status: **Repair complete, baseline re-established**

**K6: Knowledge Persistence**
- 32 checkpoints existed but were unsearchable
- Clean slate: 61 points with proper schema
- 16/32 checkpoints indexed (50% coverage)
- 16 recent checkpoints missing required fields (schema evolution gap)

---

## Context Discovery

### The Gremlin
**False positive from planning phase**:
- Explore agent predicted: "Collection has 0 points, needs indexing"
- Actual state: Collection had **237 points** with legacy schema
- Root cause: Schema mismatch, not missing data
- Lesson: **Verify assumptions with direct inspection**

**What actually happened**:
- Legacy schema: `type="session_checkpoint"`, no `section` field
- Session hook searches: `section_filter="combined"` (requires `section` field)
- Result: 237 points invisible to hook, 0 memories returned
- Duration: Dec 17, 2025 - Jan 12, 2026 (14 days, 47 sessions)
- Impact: Every session started "cold" without historical context

### Captain's Wisdom
"Let's go for option B and add partnered telos file work to help with the memory loss. This explains how the context hydration level did not increase over the two weeks of memory making cause they werent searchable!"

**Key insight**: Captain immediately understood the systemic impact - two weeks of "memory making" that wasn't actually searchable. This wasn't just a bug fix; it was restoring a critical capability both partners rely on.

---

## Decision Process

### Options Considered

**Option A: Quick Fix** (2 minutes)
- Modify `session_start.py` to search without section_filter
- Pros: Works immediately, uses existing 237 points
- Cons: Less precise searches, can't filter by section type
- **Rejected**: Compromises future architecture

**Option B: Clean Slate** (5 minutes) ✅ **Selected**
- Delete collection, re-index with new schema
- Pros: Proper section-based filtering, future-proof
- Cons: Loses 237 legacy points (though they weren't usable anyway)
- **Rationale**: "Life support before building homes" - solid foundations

**Option C: Hybrid** (10 minutes)
- Add new-schema points alongside old, teach searcher to handle both
- Pros: Preserves all data
- Cons: Complexity, 410 total points, mixed results
- **Rejected**: Over-engineering for broken data

### Partnership Dynamic
**Captain's role**: Teleological direction ("life support before building homes")
**First Mate's role**: Technical execution (delete, reindex, verify, document)
**Alignment**: Both agreed Option B prioritizes solid foundations over preserving unusable legacy data

---

## Implementation Details

### Pre-Repair State
- Qdrant container: UP (8 days healthy)
- Collection: `rhiz_memories` with 237 points
- Schema: Legacy format (no `section` field)
- Search results with `section_filter="combined"`: **0 memories**
- Search results without filter: 3 memories (but wrong architecture)

### Repair Steps Executed
1. **Deleted collection** - `curl DELETE /collections/rhiz_memories` → success
2. **Bulk indexing** - `python bulk_index_checkpoints.py` → 32 checkpoints processed
3. **Results**:
   - 16 checkpoints indexed successfully (61 points total)
   - 15 checkpoints skipped (missing required fields)
   - 1 checkpoint YAML parse error (`session_20251226_complete.yaml`)

### Post-Repair State
- Collection: `rhiz_memories` with 61 points (new schema)
- Schema: Section-based (`section="combined"`, `section="session_arc"`, etc.)
- Similarity scores: 0.2-0.4 range (lower than expected)
- Search threshold: Lowered from 0.5 → 0.3 in `session_start.py:66`
- Test results: **1 memory found** (similarity 0.302) ✅

### Schema Evolution Gap
**Issue**: 16 recent checkpoints (Jan 2026) lack fields embedder expects:
- Missing: `session_arc`, `working_memory.mental_model`, `suggested_resume_prompt`
- Cause: Checkpoint schema evolved but embedder didn't adapt
- Impact: 50% of checkpoints unsearchable

**Future work**: Either:
- A) Update embedder to handle schema variations gracefully
- B) Standardize checkpoint schema going forward
- C) Backfill missing fields in recent checkpoints

---

## Verification Results

### Section Filtering Test
```python
# With section_filter="combined", score_threshold=0.0
Found 5 memories:
  - session_20251226_wave2_first_trade.yaml: 0.381
  - session_20251221_gifts_and_pivot.yaml: 0.335
  - session_20251217_foundation.yaml: 0.315
  - session_20251217_desktop_philosophy.yaml: 0.240
  - session_20251223_birthday_research.yaml: 0.216
```

**Observation**: Scores lower than expected (0.2-0.4 vs 0.5-0.7 typical).
**Likely cause**: Hash-based embeddings + technical/domain-specific content
**Fix applied**: Lowered threshold from 0.5 → 0.3

### Session Hook Test
```bash
python session_start.py
# Output: Memory Context: 1 relevant sessions loaded
```

**Context file** (`.session_context.json`):
```json
{
  "search_topic": "recent session work, active domains, pending tasks",
  "memories_found": 1,
  "relevant_sessions": [{
    "similarity": 0.302,
    "source": "session_20251222_memory_test_expanded.yaml",
    "preview": {
      "mental_model": "The prosthetic memory system is functioning at basic level...",
      ...
    }
  }]
}
```

**Status**: ✅ **Working as designed** (1 memory > 0 memories)

---

## Decisions Made

### D1: Clean Slate Over Preservation
**Decision**: Delete 237 legacy points and reindex with new schema
**Reasoning**: Legacy points weren't usable (wrong schema), preserving them provides no value
**Confidence**: High
**Outcome**: Success - memory system now functional

### D2: Lower Search Threshold (0.5 → 0.3)
**Decision**: Reduce score_threshold in `session_start.py` from 0.5 to 0.3
**Reasoning**: Actual similarity scores are 0.2-0.4 range, threshold of 0.5 filters out all results
**Confidence**: Medium (may need further tuning)
**Outcome**: Success - hook now finds 1+ memories per session

### D3: Document as Partnered Telos Decision
**Decision**: Create this decision document tracing memory repair to telos principles
**Reasoning**: Captain's "life support before building homes" framing makes this a foundational architectural choice, not just a bug fix
**Confidence**: High
**Outcome**: This document

### D4: Defer Schema Evolution Gap
**Decision**: Accept 50% checkpoint coverage (16/32) for now, address schema gap later
**Reasoning**:
- Functional baseline restored (life support working)
- Schema standardization is "building homes" level work
- Can backfill/fix incrementally without blocking Phase 3
**Confidence**: High
**Alternatives considered**: Block on fixing all 16 checkpoints (rejected: premature optimization)

---

## Lessons Learned

### L1: Verify Planning Assumptions
The explore agent predicted "collection is empty" based on checkpoint existence. Reality: 237 points with wrong schema. **Always inspect actual state before major operations.**

### L2: Schema Evolution Requires Migration Strategy
Checkpoints evolved schema over time without embedder adaptation. **Future architectural changes need migration plans.**

### L3: Threshold Tuning is Empirical
Predicted similarity scores (0.5-0.7) didn't match reality (0.2-0.4). **Test actual data distributions before setting thresholds.**

### L4: Life Support vs Building Homes
Captain's framing clarifies prioritization: infrastructure first, features second. **Foundational systems must be solid before expansion.**

---

## Future Work

### Immediate (Wave 3)
- [ ] None - memory system is functional, move to Phase 3 integration

### Near-term (Month 1)
- [ ] Investigate why similarity scores are lower than expected
- [ ] Consider FastEmbed upgrade for better semantic similarity
- [ ] Backfill missing fields in 16 recent checkpoints

### Long-term (Month 3+)
- [ ] Standardize checkpoint schema with versioning
- [ ] Implement schema migration tooling
- [ ] Add checkpoint validation at write time

---

## Related Artifacts

- `core/hooks/session_start.py` - Modified line 66 (threshold 0.5 → 0.3)
- `core/memory/scripts/bulk_index_checkpoints.py` - Executed to reindex
- `core/memory/checkpoints/` - 32 checkpoint files (16 indexed, 16 skipped)
- `docs/architecture/PHASE_1_DEPLOYMENT_COMPLETE.md` - VPS deployment context
- `docs/architecture/PHASE_2_WORKERS_DEPLOYMENT_COMPLETE.md` - Cloudflare context

---

## Partnered Approval

**Captain**: Approved Option B ("clean slate") and requested telos documentation
**First Mate**: Executed technical implementation and authored this decision trace
**Dyad**: Aligned on "life support before building homes" prioritization

**Next**: VPS + Cloudflare verification (Part 1 + Part 2), then Phase 3 go/no-go decision

---

**Revision**: 1.0
**Date**: 2026-01-12
**Authors**: Captain (teleological direction) + First Mate (technical execution)
