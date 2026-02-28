# Rhiz Memory System Naming Conventions

## Checkpoint Files
```
session_YYYYMMDD_descriptor.yaml
```
- Date in ISO format (YYYYMMDD)
- Descriptor: lowercase, underscores, brief
- Examples:
  - `session_20251224_autonomous_exploration.yaml`
  - `session_20251223_memory_system_implementation.yaml`

## Pattern Files
```
{name}.json
```
- Lowercase, hyphens for spaces
- Descriptive but concise
- Examples:
  - `organic-minimal.json`
  - `night-walk.json`

## Memory Point IDs
Generated via `hash_id()` in ingestion scripts:
```python
def hash_id(text: str) -> int:
    return int(hashlib.md5(text.encode()).hexdigest()[:16], 16)
```

**Pattern IDs**: `pattern_{genre}_{name}`
- Example: `pattern_folk-hiphop_organic-minimal`

**Checkpoint IDs**: `{filename}_{section}`
- Example: `session_20251224_autonomous_exploration.yaml_mental_model`

## Memory Payload Types
- `musical_pattern` - Strudel patterns
- `session_arc` - Checkpoint narrative
- `mental_model` - Working memory state
- `decision` - Logged decisions with reasoning
- `resume_prompt` - Session continuation context
- `combined` - Merged embedding of multiple sections

## Sync Protocol
1. Local is working copy
2. Cloud is persistent backup
3. Sync local → cloud after significant work
4. Sync cloud → local when starting fresh session

---
*Established: December 24, 2025*
*"Initial conditions determine success"*
