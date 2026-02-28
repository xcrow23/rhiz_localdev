# Claude Grooves: Production Journal

This file tracks progress, decisions, and lessons learned throughout the project.

---

## Session 1: December 6, 2025 - MCP Foundation Complete

### Major Achievements

**MCP Integration Fully Operational**
- Successfully installed uisato/ableton-mcp-extended
- Fixed critical packaging bug (missing AbletonMCP_UDP in pyproject.toml)
- Configured Claude Desktop to communicate with Ableton Live 12
- Tested and verified: Session view reading, track discovery, device querying

**Technical Challenges Overcome**
1. **Packaging Bug**: Extended version missing AbletonMCP_UDP directory in build config
   - Fixed by adding "AbletonMCP_UDP" to packages list in pyproject.toml
   - Enables optional UDP mode for low-latency live performance (not needed for async workflow)

2. **FastMCP API Compatibility**: Server used deprecated @mcp.prompt() decorator
   - Removed FastMCP-specific features to maintain compatibility
   - Server now runs clean on standard MCP SDK

3. **Direct Server Path**: Bypassed uvx/package manager issues
   - Configured claude_desktop_config.json to run server.py directly via Python
   - More reliable for local development than packaged installation

### Current Configuration

**Claude Desktop MCP Config**
```json
{
  "mcpServers": {
    "AbletonMCP": {
      "command": "python",
      "args": ["C:\\Users\\dread\\ableton-mcp-extended\\MCP_Server\\server.py"]
    }
  }
}
```

**Ableton Setup**
- Remote Script: AbletonMCP installed in User Library/Remote Scripts
- Control Surface: Enabled in Preferences → Link, Tempo & MIDI
- Input/Output: Set to "None" (uses TCP socket, not MIDI)

**MCP Tools Available**
- `get_song_info`: Session metadata
- `get_tracks`: Track list with names/colors
- `get_track_devices`: Device chains per track
- `create_midi_clip`: Generate clips in Session View
- `create_scene`, `delete_scene`, `fire_scene`: Full scene management
- `play_song`, `stop_song`, `set_tempo`: Transport control

### Workflow Decisions

**Why uisato/ableton-mcp-extended Over Original**
- Scene management: Create/delete/fire scenes (missing in original)
- Batch operations: Edit multiple notes simultaneously
- Audio file import: Drag samples into clip slots
- More active development: 57 commits vs 23
- Only 2 open issues vs 24

**Why Direct server.py Over uvx Package**
- Immediate access to source for debugging
- No dependency on package manager updates
- Can make custom modifications if needed
- Simpler troubleshooting

### Phase 1 Checklist Progress

**Foundation (Weeks 1-2): Setup & Configuration**
- [x] Install Ableton Live 12 Trial (90 days)
- [x] Install Claude Desktop for MCP support
- [x] Install Ableton MCP (extended version with fixes)
- [x] Configure Claude Desktop MCP connection
- [x] Test MCP connection - VERIFIED WORKING
- [ ] Sign up for Soundraw free trial - IN PROGRESS
- [ ] Register for MusicAPI.ai or Soundverse
- [ ] Set up Splice account
- [ ] Create Notion workspace for project tracking
- [ ] Implement file naming convention
- [ ] Set up 3-2-1 backup (local + Backblaze)

**First Production Test: NEXT SESSION**
- [ ] Generate 10 beats using Claude + MCP
- [ ] Select best 2, import to DAW
- [ ] Record test acoustic guitar
- [ ] Record test vocals
- [ ] Create rough mix
- [ ] Document workflow pain points

### Cost Tracking

**Month 1 Baseline**
- Ableton Live 12 Trial: $0 (90 days)
- Claude Desktop: Free
- Claude API usage: TBD (first production test)
- ableton-mcp-extended: Free (MIT license)
- **Total so far: $0**

### Technical Notes

**MCP Server Architecture**
- Python-based TCP server (default port 9000)
- Communicates with Ableton via Remote Script (Python MIDI framework)
- Remote Script uses Live Object Model (LOM) API
- Claude Desktop connects via stdio, spawns server process

**Key Limitation Confirmed**
- No programmatic MIDI export via MCP
- Must manually export clips: Right-click → Export MIDI Clip
- Not a blocker for async workflow (export after session)

### Lessons Learned

1. **Extended version delivers on promises**: Scene management is essential for Session View workflow
2. **Packaging quality varies**: Open-source MCP projects may have build issues
3. **Direct source access beats convenience**: Can fix bugs immediately vs waiting for package updates
4. **MCP ecosystem still maturing**: FastMCP deprecations show API in flux

### Next Session Goals

**Beat Generation Test**
1. Craft detailed prompt for folk-hip hop beat (88 BPM, E minor)
2. Generate 3-5 variations via MCP
3. Test MIDI export workflow
4. Document time spent vs quality results
5. Identify any workflow friction

**AI Tool Setup**
- Register for Soundraw free trial
- Compare Soundraw vs MCP-generated beats
- Determine primary beat generation method

**File Organization**
- Create project folder structure per ROADMAP.md convention
- Implement naming convention: `ProjectName_Stage_Version_Type_BPM_Key_Date`
- Set up external backup drive

### Success Metrics

**Week 1 Target**: MCP integration functional ✅ COMPLETE
**Week 2 Target**: First AI-generated beat with acoustic guitar layer
**Month 1 Target**: 1 complete track (beat → guitar → vocal → mix → master)

---

## Deferred Items Log

**Not Pursuing Now (Recorded for Future Reference)**
- UDP mode configuration (only needed for live performance <10ms latency)
- ElevenLabs integration (optional AI vocal generation)
- Custom MCP development for Circuit Rhythm (Phase 4 decision point)
- GPU investment (async workflow doesn't require it)

---

## Repository Health Notes

**uisato/ableton-mcp-extended**
- Last commit: 2025 (active)
- Open issues: 2 (very manageable)
- Documentation: Excellent (INSTALLATION.md, README.md)
- Ableton 12 compatibility: Confirmed
- Production status: Stable

**Backup Plan**
- Original ahujasid/ableton-mcp available if extended version fails
- Both MIT licensed - can fork and maintain if abandoned
- Producer Pal alternative if Max for Live becomes available

---

## Captain's Log: End of Session 1

Foundation is solid. The MCP integration works exactly as needed for async production workflow. We can now command Ableton via natural language through Claude Desktop, create Session View clips, manage scenes, and control transport.

The manual MIDI export limitation is acceptable - fits naturally into the async workflow (generate overnight, export in morning review session).

Ready to generate first AI beat tomorrow. The grooves are within reach.

Next watch: Beat generation test and dual workflow comparison (MCP vs Soundraw).
