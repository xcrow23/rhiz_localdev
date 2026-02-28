# Archive Policy

**Last Updated**: 2026-01-25 (Session 73, Phase 1)

---

## Purpose

This document establishes the archival strategy for Rhiz project documentation. The goal is to preserve historical context without cluttering active documentation directories.

---

## What Gets Archived

### Point-in-Time Audits & Reports
- Comprehensive system audits (health scores, domain assessments)
- Checkpoint validation reports
- Alignment audits and issue trackers
- **Example**: `COMPREHENSIVE_ALIGNMENT_AUDIT_20260110.md`, `CHECKPOINT_AUDIT_COMPLETE.md`
- **Why**: Captures system state at specific moment; superseded by ongoing dyad.md and current status docs

### Session-Specific Fixes & Milestones
- Individual session summaries (not part of comprehensive narratives)
- Sprint/phase completion markers
- Blocker resolution logs tied to specific sessions
- **Example**: `SESSION_20_FIXES.md`, `sprint1_blocker_fixes_complete.md`, `phase2_complete.md`
- **Why**: Historical record of work progression; not reference material for current work

### Superseded Designs & Migrations
- Architecture documents for deprecated systems
- Integration documentation for migrated workflows
- Old workflow exports (n8n → Cloudflare Workers)
- **Example**: `n8n_integration.md`, `n8n_workflows_final/`
- **Why**: Migration complete; keep as historical reference for why pivot occurred

### Deprecated Components
- Documentation for removed/replaced subsystems
- Configuration guides for systems no longer in use
- **Example**: LocalAI documentation (replaced by Ollama), Hummingbot docs (replaced by Fathom)
- **Why**: Component no longer active; preserve rationale for architectural decision

---

## Archive Organization

### Quarterly Structure

```
docs/archive/
├── 2025_q4/          # Oct-Dec 2025
├── 2026_q1/          # Jan-Mar 2026
├── 2026_q2/          # Apr-Jun 2026
└── [future quarters]/
```

**Rationale**: Rhiz generates substantial documentation volume. Quarterly organization balances granularity (findable historical docs) with simplicity (not too many subdirectories).

### File Placement Rules

**By Original Date**:
- Archive files to the quarter they were created/published
- Example: Jan 10 audit → 2026_q1/, Dec 28 session → 2025_q4/

**Exceptions**:
- If migration spans quarters, archive to quarter it **completed**
- Example: n8n → Cloudflare migration (Dec-Jan) → 2026_q1/ (when mooncheck migration finished)

---

## Retention Period

**Keep Indefinitely**: All archived documentation preserved for historical reference

**Why No Deletion**:
- Failure genealogy: Understanding why approaches failed informs future decisions
- Architectural evolution: Tracking system maturity over time
- Training data: Future model instances benefit from complete project history
- Audit trail: Complete record of trust calibration and partnership evolution

**Storage Optimization**:
- If archive exceeds reasonable size (~500MB+), consider:
  - Compression of old quarters (.tar.gz)
  - Move to separate repository (rhiz_archive) with cross-references
- Not currently an issue (archive ~2MB as of Session 73)

---

## What Does NOT Get Archived

### Active Reference Documentation
- Architecture Decision Records (ADRs) for current systems
- Deployment guides for operational infrastructure
- MCP tool documentation for active tools
- **Keep in**: `docs/architecture/`, `docs/knowledge_base/`, tool READMEs

### Comprehensive Session Syntheses
- Session 72 essay (narrative compression of 39 days)
- Session 73 synthesis (architectural analysis)
- Future comprehensive syntheses
- **Keep in**: `docs/sessions/` (these are high-value compressed knowledge)

### Living Documentation
- CLAUDE.md (master project context)
- dyad.md (auto-updated system state)
- CURRENT_STATE.md (operational status)
- Session checkpoints (core/memory/checkpoints/)
- **Keep in**: Root directory, core/ subdirectories, docs/ top-level

### Foundational Research
- Skill Compression Research Synthesis
- Symbiotic Cognition framework documents
- HAIST evaluation rubrics
- **Keep in**: `docs/research/` (timeless conceptual foundations)

---

## Archive Process

### Manual Archival (Current)

**When to Archive**:
- During documentation consolidation sessions (like Phase 1)
- When major architectural pivot completes (e.g., n8n → Cloudflare)
- Quarterly review (~every 15-20 sessions)

**How to Archive**:
1. Identify obsolete documentation (point-in-time reports, superseded designs, completed milestones)
2. Determine appropriate quarter based on creation/completion date
3. Move files to `docs/archive/[quarter]/`
4. Update cross-references if needed (formal docs that reference archived files)

**Automated archival**: Not yet implemented. Consider for Phase 2 or beyond.

### Restoration Process

**When to Restore**:
- Rarely - most archived docs remain archived permanently
- Only if specific historical context needed for current decision
- Example: "Why did we pivot from Hummingbot to Fathom?" → Read archived Hummingbot docs

**How to Restore**:
1. Identify file in archive by quarter
2. Read directly from archive (no need to move back)
3. If doc becomes reference material again, copy (don't move) to active docs with update

---

## Archive Index

**As of Session 73 (Jan 25, 2026)**: 17 files archived

### 2025_q4 (Dec 2025)
- `phase1_review_synthesis.md` - SIL Phase 1 milestone
- `phase1_fixes_complete.md` - SIL Phase 1 completion
- `phase2_review_synthesis.md` - SIL Phase 2 milestone
- `phase2_complete.md` - SIL Phase 2 completion
- `sprint1_blocker_fixes_complete.md` - SIL Sprint 1 blockers resolved
- `sprint2_progress.md` - SIL Sprint 2 progress report
- `n8n_integration.md` - n8n integration doc (superseded by Cloudflare Workers)
- `SESSION_20_FIXES.md` - SIL session-specific fixes
- `SESSION_20251228_SYSTEMS_OPERATIONAL.md` - Systems operational verification (Dec 28)
- `SESSION_54_SUMMARY.md` - Session 54 summary

### 2026_q1 (Jan 2026)
- `CHECKPOINT_AUDIT_COMPLETE.md` - Checkpoint validation audit (Jan 10)
- `CHECKPOINT_AUDIT_SUMMARY.md` - Checkpoint audit summary (Jan 10)
- `CHECKPOINT_VALIDATION_REPORT.md` - Checkpoint validation results (Jan 10)
- `COMPREHENSIVE_ALIGNMENT_AUDIT_20260110.md` - System alignment audit (Jan 10)
- `FALSE_POSITIVE_AUDIT_20260110.md` - False positive analysis (Jan 10)
- `REAL_ISSUES_CLEANED_20260110.md` - Issues resolved during cleanup (Jan 10)
- `BATCH_4_COMPLETION_SUMMARY.md` - Batch 4 work completion (Jan)

---

## Cross-Reference Strategy

### If Active Doc References Archived File

**Add footnote**:
```markdown
*Historical context: See archived n8n_integration.md (docs/archive/2025_q4/) for original integration design. Superseded by Cloudflare Workers migration (Jan 2026).*
```

**Why**: Preserves continuity, explains architectural evolution without keeping obsolete doc in active directories.

### If Checkpoint References Archived Decision

**No action needed**: Checkpoints preserve historical state, including references to then-current (now-archived) documents. Archive preserves that historical accuracy.

---

## Deprecation vs Archival

**Deprecation**: Mark document as obsolete but keep in active location with clear notice
- Used when: Replacement not yet complete, transition period needed
- Example: "Future_Roadmap.md [DEPRECATED - see CURRENT_STATE.md]"

**Archival**: Move document to archive directory
- Used when: Replacement complete, doc only valuable as historical reference
- Example: n8n_integration.md → archived after Cloudflare Workers migration complete

**Workflow**: Deprecate first → Archive when replacement stable

---

## Changelog

**v1.0.0 (2026-01-25, Session 73)**:
- Initial archive policy established
- Quarterly structure defined
- 17 files archived (10 to 2025_q4, 7 to 2026_q1)
- Indefinite retention policy set

**Next Review**: April 2026 (Session ~90) or after next major architectural pivot

---

**End of Archive Policy**

*This document is living policy. Update when archival strategy changes.*
