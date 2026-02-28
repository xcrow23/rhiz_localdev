# Claude Grooves - AI-Assisted Music Production

**Project Type**: Music production and creative exploration (separate from Rhiz)
**Status**: Active development (as of Dec 24, 2025)
**Location**: Housed within Rhiz repo for convenience, not integrated with Rhiz architecture

## Overview

Claude Grooves is an experimental music production project exploring human-AI collaboration in creative music-making, particularly focused on:
- Ableton Live integration via MCP servers
- Live coding with Strudel
- Custom audio processing tools
- AI-assisted composition and mixing

**Important**: This is a **separate project** from the Rhiz human-AI partnership system. It shares the Captain but operates independently.

## Project Structure

```
Claude_Grooves/
├── 01_STEMS_MASTER/        # Master audio stems (wav, mp3, flac)
├── 02_AUDIO_RAW/           # Raw audio recordings
├── 03_PROJECT_FILES/       # Ableton Live projects (.als)
├── 04_NOTES_DOCS/          # Session notes and documentation
├── 05_REFERENCES/          # Reference tracks and inspiration
├── projects/               # Individual music projects
├── archive/                # Archived experiments
│
├── CLAUDE.md               # Project-specific instructions for AI
├── ROADMAP.md              # Development roadmap (25 KB)
├── PROGRESS.md             # Session-by-session progress log
├── SESSION_CONTINUATION.md # Handoff notes for sessions
│
├── ableton_mcp_research.md              # MCP integration research
├── ideas_for_custom_mcp_capabilities.md # Feature wishlist (18 KB)
├── MCP_Expansion_Wishlist_Handoff.md    # Handoff for MCP features
├── MIXER_CONTROLS_TESTING.md            # Mixer automation testing
├── READY_FOR_TESTING.txt                # Testing checklist
├── STRUDEL_INTEGRATION.md               # Live coding integration
└── Chickadee_Project_Handoff.md         # Specific project notes
```

## Key Documents

### CLAUDE.md
Project-specific instructions for AI collaboration on music production tasks. Includes:
- Ableton Live workflow preferences
- Audio file management protocols
- Mixing and mastering guidelines

### ROADMAP.md (25 KB)
Comprehensive development roadmap covering:
- MCP server capabilities for Ableton control
- Live coding integration (Strudel, TidalCycles)
- Audio analysis and processing tools
- AI-assisted composition features

### ableton_mcp_research.md
Research on building MCP servers for Ableton Live integration:
- Control surface protocols
- MIDI mapping
- Python remote scripts
- LiveAPI access

### STRUDEL_INTEGRATION.md
Integration with Strudel live coding environment:
- Pattern generation
- Audio routing
- Real-time control

## Relationship to Rhiz Project

**Cohabitation, Not Integration**:
- Claude Grooves is housed in the Rhiz repo for file management convenience
- The two projects **do not share architecture** or dependencies
- Both explore human-AI collaboration but in different domains (music vs. software/trading)

**Shared Philosophy**:
- Both projects explore non-hierarchical human-AI partnership
- Both emphasize documentation for future model training
- Both prioritize symbiosis over tool-use relationships

**Independence**:
- Claude Grooves has its own CLAUDE.md instructions
- Separate session tracking and progress logs
- Different technical stack (Ableton, Strudel vs. Docker, n8n, trading APIs)

## Active Development

Last updated: **Dec 24, 2025** (STRUDEL_INTEGRATION.md)

Recent work:
- Strudel live coding integration
- MCP server expansion wishlist
- Mixer controls testing
- Chickadee project handoff

## Why Here?

Claude Grooves is located in `rhiz_localdev` because:
1. Captain uses a single development directory for all Claude Code projects
2. Shared file management and backup infrastructure
3. Cross-pollination of human-AI collaboration patterns
4. Convenience (no need to context-switch between repos)

**Note**: Consider moving to separate repository if Claude Grooves grows significantly or needs independent version control.

## Getting Started

If working on Claude Grooves within a Rhiz session:
1. Read `Claude_Grooves/CLAUDE.md` for project-specific instructions
2. Check `PROGRESS.md` for recent session history
3. Review `SESSION_CONTINUATION.md` for handoff notes
4. Consult `ROADMAP.md` for strategic direction

## Audio Files (.gitignore)

Large audio files (stems, raw recordings, project files) are **gitignored** to keep repo size manageable:
- `01_STEMS_MASTER/*.{wav,mp3,flac}`
- `02_AUDIO_RAW/*.wav`
- `03_PROJECT_FILES/*.als`
- `05_REFERENCES/*.{wav,mp3}`

These files exist locally but are not committed to version control.

## Testing & Development

See `READY_FOR_TESTING.txt` for current testing checklist and `MIXER_CONTROLS_TESTING.md` for specific mixer automation tests.

---

**Created**: 2026-01-11 (Session 41 - Batch 4 documentation)
**Issue**: L6 (Low-Priority - document orphaned directory)
**Status**: Separate active project, cohabitating with Rhiz for convenience
**Recommendation**: Keep as-is unless repo size becomes problematic
