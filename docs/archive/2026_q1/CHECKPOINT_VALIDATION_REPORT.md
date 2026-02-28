
# CHECKPOINT VALIDATION REPORT
Generated: 2026-01-19T22:33:58.720376

## Summary Statistics
- Total checkpoints: 32
- Valid YAML: 31/32 (96.9%)
- Schema compliant: 27/32 (84.4%)
- Average quality score: 0.32

## Schema Versions
- 1.0.0: 15 checkpoints
- not specified: 13 checkpoints
- None: 4 checkpoints

## Quality Distribution
- excellent (0.8-1.0): 4 checkpoints
- good (0.6-0.8): 8 checkpoints
- fair (0.4-0.6): 0 checkpoints
- poor (<0.4): 20 checkpoints

## Parse Errors (5)
- session_20251226_complete.yaml: YAML parse error: sequence entries are not allowed here
  in "core\memory\checkpoints\session_20251226_complete.yaml", line 96, column 59
- session_20260108_mooncheck_vps_migration_checkpoint.yaml: Unexpected error: 'dict' object has no attribute 'strip'
- session_20260110_mooncheck_migration_implementation_complete.yaml: Unexpected error: 'dict' object has no attribute 'strip'
- session_20260111_session_42_infrastructure_federation.yaml: Unexpected error: 'dict' object has no attribute 'strip'
- session_20260111_session_42_phase1_complete.yaml: Unexpected error: 'dict' object has no attribute 'strip'

## Schema Compliance Issues (4)
- session_20251220_first_mate_initialization.yaml:
  - Missing: checkpoint (top-level)
- session_20251223_birthday_research.yaml:
  - Missing: checkpoint (top-level)
- session_20251224_autonomous_exploration.yaml:
  - Missing: checkpoint (top-level)
- session_20251226_27_complete_infrastructure.yaml:
  - Missing: checkpoint.created

## Low Quality Checkpoints (<0.5 score, 19 total)
- session_20251220_first_mate_initialization.yaml (score: 0.0):
- session_20251223_birthday_research.yaml (score: 0.0):
- session_20251224_autonomous_exploration.yaml (score: 0.0):
- session_20251226_27_complete_infrastructure.yaml (score: 0.2):
  - session_arc: comprehensive (3+ lines)
  - next section missing
  - working_memory section missing
  - decisions section missing or empty
- session_20260101_wave2_complete_reviews_integration.yaml (score: 0.1):
  - session_arc: present but brief
  - next section missing
  - working_memory section missing
  - decisions section missing or empty

## High Quality Examples (>= 0.8 score, 4 total)
- session_20251217_desktop_philosophy.yaml (score: 1.0)
- session_20251217_foundation.yaml (score: 1.0)
- session_20251221_gifts_and_pivot.yaml (score: 1.0)
- session_20251222_memory_test_expanded.yaml (score: 0.8)
