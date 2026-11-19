# Rhiz MCP Server

Unified Model Context Protocol server for the Rhiz dyad.

## Purpose

This MCP server provides bidirectional state management between Captain (human) and First Mate (AI), enabling the dyad to:
- Query each other's current state
- Update shared focus and objectives
- Track active domains and their status
- Signal blockers and completions
- Maintain dyad metrics and history

## Architecture

```
rhiz-mcp/
├── src/
│   ├── server.py          # MCP server implementation
│   ├── dyad_state.py      # Dyad state management
│   └── __init__.py
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Tools Provided

### Query Tools (Read-Only)
- `get_dyad_state` - Complete dyad state
- `get_captain_state` - Captain's current state
- `get_shared_focus` - Current shared focus
- `get_dyad_summary` - Human-readable summary

### Captain Tools
- `set_captain_state` - Update Captain availability, focus, energy, context

### First Mate Tools
- `propose_focus_shift` - Propose changing focus domain
- `signal_completion` - Signal objective completion

### Mutual Tools (Either Partner)
- `update_shared_focus` - Update domain, objective, blockers, next action
- `update_active_domain` - Update domain status
- `append_dyad_note` - Add notes to strengths/friction/evolution
- `signal_blocker` - Signal a blocker

## Installation

```bash
cd /mnt/c/Users/dread/Documents/Rhiz/origin/tools/rhiz-mcp
pip install -r requirements.txt
```

## Usage

The server is automatically invoked by Claude Code when configured in `.mcp.json`.

Manual testing:
```bash
python src/server.py
```

## State Management

The server manages `/core/daemon/dyad.md`, a system-managed document tracking:
- Dyad container state
- Captain state (availability, focus, energy, physical context)
- First Mate state (model, session, context, capabilities)
- Shared focus (domain, objective, blockers, next action)
- Active domains (trading, memory, skills, etc.)
- Dyad history and metrics

State updates are immediately written to dyad.md and available to both partners.

## Integration

This server integrates with:
- **Pattern library** (Wave 1): Patterns can reference dyad state
- **Memory system**: Session checkpoints sync with dyad state
- **Trading domain**: Fathom MCP servers report status via `update_active_domain`
- **Hooks**: Session start/end hooks update dyad state automatically

## Wave 2 Status

- [x] Dyad state schema defined
- [x] State management module
- [x] MCP server with 11 tools
- [ ] Session hooks integration
- [ ] .mcp.json configuration
- [ ] Testing with live sessions
