# MCP Server for Daemon/Dyad Infrastructure

**Status**: Placeholder directory (not yet implemented)
**Purpose**: Future home for MCP server managing dyad state and session lifecycle
**Created**: 2026-01-01
**Updated**: 2026-01-11

## Intended Architecture

This directory is reserved for an MCP server that would expose daemon/dyad state management as MCP tools, enabling:

1. **Dyad State Management**
   - Read/write dyad state (Captain + First Mate status, shared focus, metrics)
   - Update active domains, blockers, notes
   - Query dyad health and partnership metrics

2. **Session Lifecycle**
   - Session handshake coordination
   - Checkpoint triggers and validation
   - Hook execution monitoring

3. **Pattern Library Access**
   - Load patterns from `core/patterns/`
   - Pattern recognition and suggestion
   - Pattern evolution tracking

## Potential Tools (Design Phase)

If implemented, this server might expose tools like:

```python
# Dyad state tools
mcp_dyad_get_state()
mcp_dyad_update_captain_state(availability, energy, focus, physical_context)
mcp_dyad_update_shared_focus(domain, objective, blockers, next_action)
mcp_dyad_signal_blocker(description, severity)
mcp_dyad_append_note(category, note)

# Session lifecycle tools
mcp_session_handshake(previous_checkpoint_id)
mcp_session_checkpoint_validate(checkpoint_data)
mcp_session_get_context()

# Pattern library tools
mcp_pattern_load(pattern_name)
mcp_pattern_suggest(current_context)
mcp_pattern_record_usage(pattern_name, effectiveness)
```

## Current Implementation

**Dyad state management** is currently handled by:
- `core/daemon/dyad.md` - YAML-based state file
- `core/hooks/session_start.py` - Updates dyad state on session start
- `tools/rhiz-mcp/` - Existing MCP server with dyad state tools:
  - `get_dyad_state`
  - `get_captain_state`
  - `set_captain_state`
  - `update_shared_focus`
  - `signal_blocker`
  - `append_dyad_note`
  - etc. (11 dyad-related tools total)

**Conclusion**: The dyad MCP tools already exist in `tools/rhiz-mcp/`. This directory may have been a placeholder for an alternative implementation or modular separation of concerns.

## Recommendation

Two paths forward:

1. **Keep as placeholder**: Reserve for future modular architecture where daemon functionality is separated from rhiz-mcp
2. **Remove directory**: Consolidate all MCP servers under `tools/` for clarity

**Current Decision**: Keep as documented placeholder until architectural review determines need for separation.

## Related Files

- `core/daemon/dyad.md` - Dyad state storage (YAML)
- `core/daemon/dyadic_patterns_library.md` - Pattern definitions
- `tools/rhiz-mcp/src/tools/dyad.py` - Current dyad MCP implementation
- `core/hooks/session_start.py` - Dyad state initialization
- `core/hooks/session_end.py` - Session cleanup

---

**Created**: 2026-01-11 (Session 41 - Batch 4 cleanup)
**Issue**: M7 (Medium-Priority)
**Action**: Document placeholder status, clarify existing implementation
