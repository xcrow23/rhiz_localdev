# Checkpoint System Improvements - Implementation Guide

**Purpose:** Prevent quality degradation, enforce schema compliance, enable automated repair
**Target:** Achieve consistent 0.8+ quality scores across all checkpoints
**Timeline:** Phased implementation (immediate → short-term → medium-term)

---

## Phase 1: Immediate Fixes (This Session)

### Fix 1.1: Repair Critical YAML Error

**File:** `core/memory/checkpoints/session_20251226_complete.yaml`
**Line 96:** Quote mismatch breaking YAML parsing

**Current (BROKEN):**
```yaml
key_insights:
  - "BTC as learning platform (tight margins = precision training)"
  - "Most intelligent trader between us (that's you)" - delegating strategy
  - "Slack approval workflow" - maintaining oversight on >$20 orders
```

**Fixed:**
```yaml
key_insights:
  - "BTC as learning platform (tight margins = precision training)"
  - "Most intelligent trader between us (that's you) - delegating strategy"
  - "Slack approval workflow - maintaining oversight on >$20 orders"
```

**Action:** Edit line 96, remove quote after "you)", include "- delegating strategy" in string

### Fix 1.2: Update Validation Script

**File:** `validate_checkpoints.py`
**Line 49-56:** Handle session_arc as string OR dict

**Current code assumes string:**
```python
session_arc = checkpoint.get("session_arc", "")
if session_arc:
    arc_lines = session_arc.strip().split("\n")  # BREAKS if dict
```

**Updated code:**
```python
session_arc = checkpoint.get("session_arc", "")

# Handle both string and dict formats
if isinstance(session_arc, dict):
    # Extract narrative from dict structure
    narrative_parts = [
        session_arc.get("opening", ""),
        str(session_arc.get("key_developments", "")),
        session_arc.get("current_state", ""),
        session_arc.get("trajectory", "")
    ]
    arc_text = "\n".join([p for p in narrative_parts if p])
    arc_lines = arc_text.split("\n")
elif isinstance(session_arc, str):
    arc_lines = session_arc.strip().split("\n")
else:
    arc_lines = []

if len(arc_lines) >= 3:
    quality_points += 2
    result["quality_notes"].append("session_arc: comprehensive (3+ lines)")
elif len(arc_lines) >= 1:
    quality_points += 1
    result["quality_notes"].append("session_arc: present but brief")
else:
    result["quality_notes"].append("session_arc: missing or empty")
```

---

## Phase 2: Enhanced Validation (This Week)

### Enhancement 2.1: Add Quality Validation to write_checkpoint

**File:** `tools/rhiz-mcp/src/checkpoint_manager.py`
**Add new method after line 200:**

```python
def assess_quality(self, checkpoint_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Assess checkpoint quality before writing.

    Returns:
        {
            "score": float,  # 0.0-1.0
            "missing_sections": List[str],
            "warnings": List[str],
            "recommendations": List[str]
        }
    """
    quality = {
        "score": 0.0,
        "missing_sections": [],
        "warnings": [],
        "recommendations": []
    }

    points = 0
    max_points = 10

    # Check session_arc (2 points)
    checkpoint = checkpoint_data.get("checkpoint", {})
    session_arc = checkpoint.get("session_arc", "")

    if isinstance(session_arc, dict):
        # Dict format
        has_content = any([
            session_arc.get("opening"),
            session_arc.get("key_developments"),
            session_arc.get("current_state"),
            session_arc.get("trajectory")
        ])
        if has_content:
            points += 2
        else:
            quality["missing_sections"].append("session_arc (empty dict)")
    elif isinstance(session_arc, str) and len(session_arc.strip()) > 100:
        points += 2
    else:
        quality["missing_sections"].append("session_arc (brief or missing)")

    # Check suggested_resume_prompt (2 points)
    max_points += 2
    if "next" in checkpoint_data:
        resume_prompt = checkpoint_data["next"].get("suggested_resume_prompt", "")
        if len(resume_prompt) > 100:
            points += 2
        else:
            quality["missing_sections"].append("suggested_resume_prompt")
    else:
        quality["missing_sections"].append("next section")

    # Check mental_model (2 points)
    max_points += 2
    if "working_memory" in checkpoint_data:
        mental_model = checkpoint_data["working_memory"].get("mental_model", "")
        if len(mental_model) > 100:
            points += 2
        else:
            quality["missing_sections"].append("mental_model")
    else:
        quality["missing_sections"].append("working_memory section")

    # Check decisions (2 points)
    max_points += 2
    if "decisions" in checkpoint_data and isinstance(checkpoint_data["decisions"], list):
        decisions = checkpoint_data["decisions"]
        has_alternatives = any(d.get("alternatives_rejected") for d in decisions)
        if has_alternatives:
            points += 2
        elif decisions:
            points += 1
            quality["warnings"].append("decisions present but no alternatives documented")
        else:
            quality["missing_sections"].append("decisions (empty)")
    else:
        quality["missing_sections"].append("decisions section")

    # Check progress narrative (1 point)
    max_points += 1
    if "progress" in checkpoint_data:
        narrative = checkpoint_data["progress"].get("narrative", "")
        if len(narrative) > 50:
            points += 1
    else:
        quality["missing_sections"].append("progress section")

    # Check artifacts (1 point)
    max_points += 1
    if "artifacts" in checkpoint_data and checkpoint_data["artifacts"]:
        points += 1
    else:
        quality["warnings"].append("no artifacts documented")

    quality["score"] = round(points / max_points, 2)

    # Generate recommendations
    if quality["score"] < 0.5:
        quality["recommendations"].append(
            "LOW QUALITY: Consider adding missing sections before session end"
        )
    if "suggested_resume_prompt" in quality["missing_sections"]:
        quality["recommendations"].append(
            "Add suggested_resume_prompt: 3-5 sentences for next session context"
        )
    if "mental_model" in quality["missing_sections"]:
        quality["recommendations"].append(
            "Add mental_model: How you understand the system/problem now"
        )
    if "decisions" in quality["missing_sections"]:
        quality["recommendations"].append(
            "Document decisions: What was decided and why (with alternatives rejected)"
        )

    return quality


def write_checkpoint(self, checkpoint_data: Dict[str, Any],
                    description: Optional[str] = None,
                    validate_quality: bool = True) -> str:
    """
    Write a new checkpoint file with optional quality validation.

    Args:
        checkpoint_data: The checkpoint data to write
        description: Optional description for filename
        validate_quality: If True, assess quality and warn if low

    Returns:
        Filename of written checkpoint
    """
    # Quality assessment (NEW)
    if validate_quality:
        quality = self.assess_quality(checkpoint_data)

        if quality["score"] < 0.5:
            print(f"\n⚠️  WARNING: Checkpoint quality score is LOW ({quality['score']:.2f})")
            print("\nMissing sections:")
            for section in quality["missing_sections"]:
                print(f"  - {section}")

            print("\nRecommendations:")
            for rec in quality["recommendations"]:
                print(f"  - {rec}")

            print("\nProceed anyway? (checkpoint will be written)")

    # [Existing write_checkpoint code continues...]
    # Generate filename
    timestamp = datetime.now()
    # ... rest of existing implementation
```

**Usage:** Quality check runs automatically, warns if score < 0.5, but still writes checkpoint

### Enhancement 2.2: Create Checkpoint Repair Script

**New File:** `tools/repair_checkpoint.py`

```python
"""
Checkpoint Repair Tool

Automatically repairs common checkpoint issues:
- YAML syntax errors
- Missing required fields
- Format inconsistencies
"""

import yaml
import shutil
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

CHECKPOINT_DIR = Path("core/memory/checkpoints")


def backup_checkpoint(checkpoint_path: Path) -> Path:
    """Create backup before repair."""
    backup_path = checkpoint_path.with_suffix(".yaml.backup")
    shutil.copy2(checkpoint_path, backup_path)
    return backup_path


def repair_yaml_syntax(checkpoint_path: Path) -> Dict[str, Any]:
    """
    Attempt to repair common YAML syntax errors.

    Returns repair report.
    """
    report = {
        "file": checkpoint_path.name,
        "repairs": [],
        "errors": [],
        "success": False
    }

    try:
        # Read original
        with open(checkpoint_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Common repairs
        repaired_content = content

        # Fix 1: Quote mismatches in list items
        # Example: - "text" - more text  →  - "text - more text"
        import re
        pattern = r'^(\s*-\s*"[^"]+")(\s*-\s*.+)$'
        lines = repaired_content.split('\n')
        for i, line in enumerate(lines):
            match = re.match(pattern, line)
            if match:
                before_quote = match.group(1)
                after_dash = match.group(2).strip('- ').strip()
                lines[i] = f'{before_quote[:-1]} {after_dash}"'
                report["repairs"].append(f"Line {i+1}: Fixed quote mismatch in list item")

        repaired_content = '\n'.join(lines)

        # Validate repaired YAML
        try:
            yaml.safe_load(repaired_content)
            report["success"] = True
            report["repairs"].append("YAML now parses successfully")

            # Write repaired version
            with open(checkpoint_path, 'w', encoding='utf-8') as f:
                f.write(repaired_content)

        except yaml.YAMLError as e:
            report["errors"].append(f"Still has YAML errors after repair: {e}")

    except Exception as e:
        report["errors"].append(f"Repair failed: {e}")

    return report


def add_missing_fields(checkpoint_data: Dict[str, Any],
                      checkpoint_path: Path) -> Dict[str, Any]:
    """Add commonly missing required fields."""
    report = {
        "fields_added": [],
        "warnings": []
    }

    checkpoint = checkpoint_data.get("checkpoint", {})

    # Add schema_version if missing
    if "schema_version" not in checkpoint:
        checkpoint["schema_version"] = "1.0.0"
        report["fields_added"].append("schema_version: 1.0.0")

    # Add created timestamp if missing
    if "created" not in checkpoint:
        # Use file modification time
        file_stat = checkpoint_path.stat()
        created = datetime.fromtimestamp(file_stat.st_mtime).isoformat()
        checkpoint["created"] = created
        report["fields_added"].append(f"created: {created} (from file metadata)")

    # Wrap in checkpoint structure if missing
    if "checkpoint" not in checkpoint_data:
        checkpoint_data = {"checkpoint": checkpoint_data}
        report["fields_added"].append("Added top-level checkpoint wrapper")

    return report


def repair_checkpoint(checkpoint_path: Path,
                     dry_run: bool = False) -> Dict[str, Any]:
    """
    Attempt comprehensive checkpoint repair.

    Args:
        checkpoint_path: Path to checkpoint file
        dry_run: If True, don't write changes

    Returns:
        Repair report
    """
    report = {
        "file": checkpoint_path.name,
        "backup_created": None,
        "yaml_repairs": None,
        "field_additions": None,
        "final_status": "unknown",
        "dry_run": dry_run
    }

    # Create backup
    if not dry_run:
        backup_path = backup_checkpoint(checkpoint_path)
        report["backup_created"] = str(backup_path)

    # Step 1: Repair YAML syntax
    yaml_report = repair_yaml_syntax(checkpoint_path)
    report["yaml_repairs"] = yaml_report

    if not yaml_report["success"]:
        report["final_status"] = "failed_yaml_repair"
        return report

    # Step 2: Add missing fields
    try:
        with open(checkpoint_path, 'r', encoding='utf-8') as f:
            checkpoint_data = yaml.safe_load(f)

        field_report = add_missing_fields(checkpoint_data, checkpoint_path)
        report["field_additions"] = field_report

        if not dry_run and field_report["fields_added"]:
            # Write updated checkpoint
            with open(checkpoint_path, 'w', encoding='utf-8') as f:
                yaml.dump(checkpoint_data, f,
                         default_flow_style=False,
                         allow_unicode=True,
                         sort_keys=False)

        report["final_status"] = "success"

    except Exception as e:
        report["final_status"] = "failed_field_addition"
        report["error"] = str(e)

    return report


def main():
    """Repair all checkpoints with issues."""
    print("Checkpoint Repair Tool\n")

    # Find checkpoints with known issues
    issues = [
        "session_20251226_complete.yaml",  # YAML syntax
        "session_20251220_first_mate_initialization.yaml",  # Missing wrapper
        "session_20251223_birthday_research.yaml",  # Missing wrapper
        "session_20251224_autonomous_exploration.yaml",  # Missing wrapper
        "session_20251226_27_complete_infrastructure.yaml",  # Missing created
    ]

    for filename in issues:
        checkpoint_path = CHECKPOINT_DIR / filename

        if not checkpoint_path.exists():
            print(f"⚠️  {filename}: File not found")
            continue

        print(f"\nRepairing {filename}...")

        # Dry run first
        report = repair_checkpoint(checkpoint_path, dry_run=True)

        print(f"  Dry run status: {report['final_status']}")

        if report['yaml_repairs'] and report['yaml_repairs']['repairs']:
            print("  YAML repairs:")
            for repair in report['yaml_repairs']['repairs']:
                print(f"    - {repair}")

        if report['field_additions'] and report['field_additions']['fields_added']:
            print("  Fields to add:")
            for field in report['field_additions']['fields_added']:
                print(f"    - {field}")

        # Confirm before actual repair
        confirm = input("\n  Apply repairs? (y/n): ")

        if confirm.lower() == 'y':
            report = repair_checkpoint(checkpoint_path, dry_run=False)
            print(f"  ✅ Repair complete: {report['final_status']}")
            if report['backup_created']:
                print(f"  📁 Backup: {report['backup_created']}")
        else:
            print("  ⏭️  Skipped")


if __name__ == "__main__":
    main()
```

---

## Phase 3: Schema Update (This Week)

### Update 3.1: Create Schema v1.1.0

**File:** `core/memory/session_schema_v1.1.0.yaml`

**Key additions:**

```yaml
schema_version: "1.1.0"

# CHANGELOG from v1.0.0:
# - session_arc now supports both string and dict formats
# - Added optional session_metadata section
# - Added optional quality_assessment section
# - Explicit required vs recommended vs optional field documentation

checkpoint:
  # REQUIRED FIELDS
  created: "YYYY-MM-DD HH:MM" or ISO8601
  session_id: "session_YYYYMMDD_description"
  session_arc:
    # Option 1: Original string format (backward compatible)
    type: string
    example: |
      Multi-line narrative summary.
      Session started with X, discovered Y, pivoted to Z.

    # Option 2: Structured format (v1.1.0+)
    type: object
    properties:
      opening: "Session context and starting conditions"
      key_developments:
        - "Major development 1"
        - "Major development 2"
      current_state: "State at session end"
      trajectory: "Where we're heading next"

  # OPTIONAL: Session metadata for tracking
  session_metadata:  # NEW in v1.1.0
    session_id: "unique_session_identifier"
    wave: "wave_name_if_applicable"
    date: "YYYY-MM-DD"
    duration_hours: number
    status: "checkpoint_type"

  # OPTIONAL: Quality self-assessment
  quality_assessment:  # NEW in v1.1.0
    completeness: "high | medium | low"
    resume_readiness: "excellent | good | fair | poor"
    notes: "Optional quality notes or known gaps"

# RECOMMENDED FIELDS (warn if missing)
next:
  immediate: ["next action 1", "next action 2"]
  suggested_resume_prompt: |
    Rich narrative prompt (3-5 sentences) providing
    context to continue naturally.

working_memory:
  mental_model: |
    How we understand the system/problem.
    Key relationships and mechanisms.

progress:
  status: "not_started | in_progress | blocked | completed"

# OPTIONAL FIELDS (no warning if missing)
decisions: []
artifacts: []
context: {}
training_annotations: {}
```

---

## Phase 4: Session Hook Integration (This Month)

### Hook 4.1: Pre-Session Checkpoint Quality Check

**File:** `core/hooks/session_end.py` (create if doesn't exist)

```python
"""
Session End Hook

Validates checkpoint quality before session termination.
"""

from pathlib import Path
import sys

# Add rhiz-mcp to path
sys.path.append(str(Path(__file__).parent.parent.parent / "tools" / "rhiz-mcp" / "src"))

from checkpoint_manager import CheckpointManager


def validate_session_end_checkpoint(checkpoint_data):
    """
    Hook called before session end to validate checkpoint quality.

    Returns:
        - True: checkpoint acceptable, proceed
        - False: checkpoint needs improvement
    """
    manager = CheckpointManager()

    # Assess quality
    quality = manager.assess_quality(checkpoint_data)

    print("\n" + "="*60)
    print("SESSION END CHECKPOINT QUALITY ASSESSMENT")
    print("="*60)
    print(f"\nQuality Score: {quality['score']:.2f}/1.0")

    if quality["score"] >= 0.8:
        print("Status: ✅ EXCELLENT - Ready for session end")
        return True

    elif quality["score"] >= 0.6:
        print("Status: ✔️  GOOD - Acceptable quality")
        return True

    elif quality["score"] >= 0.4:
        print("Status: ⚠️  FAIR - Consider improving before session end")

        if quality["missing_sections"]:
            print("\nMissing sections:")
            for section in quality["missing_sections"]:
                print(f"  - {section}")

        if quality["recommendations"]:
            print("\nRecommendations:")
            for rec in quality["recommendations"]:
                print(f"  - {rec}")

        return True  # Allow but warn

    else:
        print("Status: ❌ POOR - Strongly recommend improving")

        if quality["missing_sections"]:
            print("\nCritically missing:")
            for section in quality["missing_sections"]:
                print(f"  - {section}")

        print("\nThis checkpoint may not provide enough context for session resumption.")
        print("Consider adding:")
        print("  1. Comprehensive session_arc (what happened and why)")
        print("  2. Suggested resume prompt (how to continue)")
        print("  3. Mental model (current understanding)")
        print("  4. Decisions made (with alternatives rejected)")

        return False  # Block session end
```

---

## Implementation Checklist

### Phase 1: Immediate ✅
- [ ] Repair `session_20251226_complete.yaml` line 96 YAML error
- [ ] Update `validate_checkpoints.py` to handle dict session_arc
- [ ] Re-run validation to confirm all parse errors resolved

### Phase 2: This Week 🔧
- [ ] Add `assess_quality()` method to checkpoint_manager.py
- [ ] Update `write_checkpoint()` to validate quality before writing
- [ ] Create `repair_checkpoint.py` script
- [ ] Run repair script on 5 checkpoints with known issues
- [ ] Re-validate all checkpoints after repairs

### Phase 3: This Week 📋
- [ ] Create `session_schema_v1.1.0.yaml`
- [ ] Document schema changes in CHANGELOG
- [ ] Update CLAUDE.md with schema version reference
- [ ] Test schema with both string and dict session_arc formats

### Phase 4: This Month 🔗
- [ ] Create `core/hooks/session_end.py`
- [ ] Integrate hook with Claude Code session lifecycle
- [ ] Test hook with low-quality checkpoint (should warn)
- [ ] Test hook with high-quality checkpoint (should pass)
- [ ] Document hook usage in CLAUDE.md

---

## Success Metrics

**Target:** 80% of checkpoints scoring ≥0.8 quality within 1 month

**Tracking:**
- Weekly quality score average
- % checkpoints with all recommended sections
- Parse error rate (target: 0%)
- Schema compliance rate (target: 100%)

**Dashboard:** Create weekly quality report showing trends

---

## Long-Term Vision

**Automated Checkpoint Curation:**
1. Session hook validates quality before end
2. Missing sections auto-suggested based on session content
3. Template pre-populated with detected artifacts/decisions
4. Quality feedback loop prevents degradation
5. Repair tools fix legacy checkpoints automatically

**Result:** Every checkpoint is resume-ready, comprehensive, and maintains 45-year foundation standards.
