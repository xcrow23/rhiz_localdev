# Rhiz Memory Browser

Interactive CLI tool for exploring Qdrant vector memories in the Rhiz project.

---

## Features

- **Collection Info**: View statistics about the memory collection
- **List Memories**: Browse memories with optional filtering
- **Semantic Search**: Search memories by meaning (uses Qdrant query)
- **Get by ID**: Retrieve specific memory by ID
- **Export**: Export all memories to JSON

---

## Requirements

- Qdrant running at `localhost:6333`
- Python 3.x (uses only stdlib - no dependencies!)

---

## Usage

```bash
cd /mnt/c/Users/dread/Documents/Rhiz_LocalDev/tools/memory-browser

# Show collection info
python3 rhiz_memory_browser.py info

# List memories
python3 rhiz_memory_browser.py list -n 10

# List with type filter
python3 rhiz_memory_browser.py list -t musical_pattern -n 5

# Show detailed view
python3 rhiz_memory_browser.py list -n 3 --detailed

# Semantic search
python3 rhiz_memory_browser.py search "introspective night"

# Search with detailed results
python3 rhiz_memory_browser.py search "folk music" --detailed

# Get specific memory by ID
python3 rhiz_memory_browser.py get 1607618279801023273

# Export all memories to JSON
python3 rhiz_memory_browser.py export memories_backup.json

# Export with type filter
python3 rhiz_memory_browser.py export musical_patterns.json -t musical_pattern
```

---

## Commands

### `info`
Show collection statistics including:
- Total memory count
- Indexed vectors
- Vector dimensions
- Distance metric

### `list`
Browse memories with options:
- `-n, --limit N` - Number to show (default: 10)
- `-t, --type TYPE` - Filter by memory type
- `-d, --detailed` - Show full details instead of summary

### `search`
Semantic search across memories:
- `query` - Search query text
- `-n, --limit N` - Number of results (default: 5)
- `-d, --detailed` - Show full details

### `get`
Retrieve specific memory:
- `id` - Memory ID (from list or search)

### `export`
Export memories to JSON file:
- `output` - Output file path
- `-t, --type TYPE` - Filter by type

---

## Current Collection State

As of 2025-12-25:
- **Total memories**: 93
- **Type**: musical_pattern (from Strudel MCP)
- **Vector size**: 384 (sentence transformers)
- **Source**: Alex's Strudel patterns gift to Rhiz

### Memory Structure
```json
{
  "id": 1607618279801023273,
  "payload": {
    "type": "musical_pattern",
    "name": "front-porch",
    "genre": "folk-hiphop",
    "bpm": 90,
    "key": "C",
    "description": "...",
    "tags": ["folk-hiphop", "acoustic-forward"],
    "pattern_code": "setcpm(90)...",
    "source_file": "...",
    "timestamp": "2025-12-24T14:00:00.000Z",
    "ingested_at": "2025-12-25T03:32:25.034866"
  }
}
```

---

## Future Enhancements

Potential improvements for future sessions:
- [ ] Add filtering by date range
- [ ] Support multiple collections
- [ ] Batch operations (delete, update)
- [ ] Interactive TUI mode (ncurses)
- [ ] Vector visualization (PCA/t-SNE projection)
- [ ] Memory analytics (clustering, similarity graphs)
- [ ] Integration with Fathom (trade memory browsing)

---

## Architecture

**Zero dependencies** - Uses only Python stdlib:
- `urllib.request` for HTTP
- `json` for parsing
- `argparse` for CLI

This keeps it lightweight and portable.

---

## Integration with Rhiz

This tool is part of the Rhiz memory infrastructure:

```
Qdrant (Docker)
    ↓
rhiz_memory_browser.py
    ↓
Export → memories_export.json → Long-term archival
```

Future: Can add direct integration with:
- Fathom MCP (browse trade memories)
- Session Checkpoint API (browse session memories)
- HAIST scoring (analyze exemplary sessions)

---

## Examples

### Browse Recent Memories
```bash
python3 rhiz_memory_browser.py list -n 10
```

### Find Introspective Patterns
```bash
python3 rhiz_memory_browser.py search "introspective contemplative" -n 5 --detailed
```

### Export All Musical Patterns
```bash
python3 rhiz_memory_browser.py export strudel_backup_20251225.json -t musical_pattern
```

### Get Full Details of Specific Memory
```bash
python3 rhiz_memory_browser.py get 5709927530412116594
```

---

## Development

Built in 1 hour as autonomous second project during Fathom Phase 1 session (2025-12-25).

**Design philosophy**: Simple, direct, useful. No over-engineering.

---

Built with 🐙 by First Mate (Claude Code)
Status: ✅ COMPLETE
Collection: rhiz_memories (93 points)
