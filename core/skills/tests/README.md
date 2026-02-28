# Skill Routing Test Suite

Comprehensive test coverage for the Rhiz semantic skill routing system.

## Test Structure

```
tests/
├── conftest.py                    # Shared fixtures and utilities
├── test_router.py                 # Unit tests (fast, no dependencies)
├── test_router_integration.py     # Integration tests (requires Qdrant)
├── test_router_accuracy.py        # Golden test set (accuracy validation)
└── README.md                      # This file
```

## Running Tests

### Prerequisites

1. **Qdrant running locally**:
   ```bash
   docker ps | grep qdrant
   # Should show qdrant container running on port 6333
   ```

2. **Skills collection ingested**:
   ```bash
   python core/skills/scripts/initialize_skills_collection.py
   python core/skills/scripts/ingest_skills.py
   ```

3. **Install pytest** (if not already installed):
   ```bash
   pip install pytest pytest-cov
   ```

### Run All Tests

```bash
# From rhiz_localdev root directory
pytest core/skills/tests/ -v
```

### Run by Test Type

**Unit tests only** (fast, no external dependencies):
```bash
pytest core/skills/tests/ -v -m unit
```

**Integration tests** (requires Qdrant):
```bash
pytest core/skills/tests/ -v -m integration
```

**Accuracy tests** (golden test set):
```bash
pytest core/skills/tests/ -v -m accuracy
```

### Run Specific Test Files

```bash
# Unit tests
pytest core/skills/tests/test_router.py -v

# Integration tests
pytest core/skills/tests/test_router_integration.py -v

# Accuracy tests (golden set)
pytest core/skills/tests/test_router_accuracy.py -v
```

### Run with Coverage

```bash
pytest core/skills/tests/ --cov=core.skills.router --cov-report=html
```

Coverage report will be in `htmlcov/index.html`

## Test Categories

### Unit Tests (`test_router.py`)

Tests core router logic in isolation:
- Initialization and error handling
- Input validation (empty queries, invalid thresholds, invalid limits)
- Route query functionality
- Metadata caching
- Edge cases (unicode, long queries, special characters)

**Markers**: `@pytest.mark.unit`
**Dependencies**: None (can run without Qdrant)
**Speed**: Fast (<1s total)

### Integration Tests (`test_router_integration.py`)

Tests full stack integration:
- MCP server singleton pattern
- End-to-end routing through MCP interface
- Domain context boosting
- Performance benchmarks
- Concurrent request handling

**Markers**: `@pytest.mark.integration`
**Dependencies**: Qdrant running, skills collection ingested
**Speed**: Medium (2-5s total)

### Accuracy Tests (`test_router_accuracy.py`)

Tests routing accuracy against golden test set:
- 30 carefully selected queries across all skill domains
- Target accuracy: 85-90% (26-27 correct matches)
- Confidence distribution analysis
- Candidate ranking quality
- Regression prevention

**Markers**: `@pytest.mark.accuracy`
**Dependencies**: Qdrant running, skills collection ingested
**Speed**: Medium (3-5s total)

## Golden Test Set

The accuracy tests use a golden test set of 30 queries:

- **Trading queries** (8): Direct Kraken operations, analysis
- **Memory queries** (8): Checkpoint retrieval, session management
- **Infrastructure queries** (6): Deployment, monitoring
- **Research queries** (4): Documentation, analysis
- **Edge cases** (4): Ambiguous queries, fallback testing

**Current Baseline Accuracy**: Target 85-90%
**Threshold**: 0.45 (empirically tuned)

## Interpreting Results

### Success Criteria

✅ **All tests pass**: System is working correctly
✅ **Accuracy ≥85%**: Routing quality meets target
✅ **Performance <100ms**: Routing is fast enough for interactive use

### Failure Scenarios

❌ **Unit tests fail**: Core logic broken - fix before proceeding
❌ **Integration tests fail**: MCP integration issue - check singleton pattern
❌ **Accuracy <85%**: Routing quality degraded:
  - Check threshold tuning
  - Review skill fingerprints (utterances, descriptions)
  - Analyze failure patterns in accuracy report

### Accuracy Report

The accuracy tests generate a detailed report showing:
- Overall accuracy percentage
- Category breakdown (trading, memory, infrastructure, research)
- Individual query failures with expected vs actual
- Candidate ranking for mismatches

Example output:
```
================================================================================
GOLDEN TEST SET ACCURACY REPORT
================================================================================
Total Queries: 30
Correct Matches: 26
Accuracy: 86.7%
Threshold: 0.45
================================================================================

Category Breakdown:
  Trading: 7/8 (87.5%)
  Memory: 7/8 (87.5%)
  Infrastructure: 6/6 (100.0%)
  Research: 4/4 (100.0%)
  Edge: 2/4 (50.0%)
================================================================================
```

## Continuous Testing

### Pre-commit Testing

Run unit tests before committing:
```bash
pytest core/skills/tests/test_router.py -v
```

### Pre-deployment Testing

Run full suite before deploying changes:
```bash
pytest core/skills/tests/ -v
```

### Accuracy Regression Testing

Run golden test set weekly to catch accuracy drift:
```bash
pytest core/skills/tests/test_router_accuracy.py -v
```

## Adding New Tests

### Adding a Unit Test

1. Edit `test_router.py`
2. Add test method to appropriate test class
3. Mark with `@pytest.mark.unit`
4. Ensure test is isolated (no Qdrant dependency)

### Adding to Golden Test Set

1. Edit `test_router_accuracy.py`
2. Add query → expected_skill mapping to `GOLDEN_TEST_SET`
3. Ensure query represents real usage pattern
4. Re-run accuracy tests to verify

### Adding an Integration Test

1. Edit `test_router_integration.py`
2. Add test method to appropriate test class
3. Mark with `@pytest.mark.integration`
4. Use `skill_router` or `mcp_server_context` fixtures

## Troubleshooting

### "rhiz_skills collection not found"

```bash
# Initialize and ingest skills
python core/skills/scripts/initialize_skills_collection.py
python core/skills/scripts/ingest_skills.py
```

### "Cannot connect to Qdrant"

```bash
# Check Qdrant is running
docker ps | grep qdrant

# If not running, start it
docker start qdrant
```

### "Module 'core.skills.router' not found"

```bash
# Ensure RHIZ_ROOT is set or run from project root
cd C:\Users\dread\Documents\Rhiz_LocalDev
pytest core/skills/tests/ -v
```

### Accuracy tests failing

1. Check threshold: Default is 0.45, may need tuning
2. Review skill fingerprints: Ensure utterances are representative
3. Analyze failure report: Look for patterns in mismatches
4. Consider expanding utterances for failing skills

## Test Maintenance

- **Weekly**: Run golden test set to check for accuracy drift
- **Before releases**: Run full test suite with coverage
- **After skill changes**: Re-run accuracy tests to verify no regression
- **When adding skills**: Update golden test set with new queries

## Coverage Goals

- **Unit tests**: 100% coverage of router.py core logic
- **Integration tests**: 100% coverage of MCP tool interface
- **Accuracy tests**: 85-90% accuracy on golden test set

## Related Documentation

- `core/skills/router.py` - Router implementation with threshold rationale
- `CLAUDE.md` - Deployment strategy and architecture notes
- `core/skills/registry/skill_fingerprints.yaml` - Skill definitions
