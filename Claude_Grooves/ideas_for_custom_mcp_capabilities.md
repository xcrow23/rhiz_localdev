# Custom Ableton MCP Capabilities - Ideas

## Overview
Potential custom tools for extending the Ableton MCP server to support the Claude Grooves async folk-hip hop production workflow.

## Proposed Custom Tools

### 1. Batch Beat Generation
```python
@mcp.tool()
async def batch_generate_beats(count: int, bpm_range: tuple, key: str) -> str:
    """Queue overnight API requests to Soundraw/MusicAPI.ai.

    Args:
        count: Number of beats to generate
        bpm_range: (min, max) BPM range (e.g., (80, 95) for folk-hip hop)
        key: Musical key (e.g., "Em", "Am")

    Returns:
        Job ID for batch processing status
    """
```

### 2. Dual Output Export
```python
@mcp.tool()
async def export_dual_output(project_name: str, bpm: int, key: str, date: str) -> str:
    """Auto-export both streaming mix and Circuit Rhythm backing track.

    Exports:
    1. Streaming: -10 LUFS, -1.5 dBTP, WAV 24-bit/48kHz
    2. Live backing: mono WAV 48kHz, max 220s per pack

    Naming: ProjectName_MIX_v3_INST_088_Em_20251115.wav

    Args:
        project_name: Track name
        bpm: Tempo (80-95 recommended)
        key: Musical key
        date: YYYYMMDD format
    """
```

### 3. Folk-Hip Hop Template
```python
@mcp.tool()
async def apply_folk_hiphop_template() -> str:
    """Apply genre-specific production settings.

    Automatically configures:
    - Acoustic guitar: HPF @80-100Hz, boost @3-5kHz
    - 808 bass: Sidechain to kick (3-6dB ducking)
    - All electronic elements: Matching room reverb (0.5-1.5s decay)
    """
```

### 4. Frequency Space Verification
```python
@mcp.tool()
async def verify_freq_space(guitar_track: int, bass_track: int) -> dict:
    """Check for 808/guitar frequency conflicts before recording.

    Returns:
        {
            "conflict_detected": bool,
            "guitar_low_freq": int,
            "bass_peak_freq": int,
            "recommendation": str
        }
    """
```

### 5. Stem Organization
```python
@mcp.tool()
async def organize_stems(source_dir: str, project_name: str) -> str:
    """Auto-rename and organize exported stems per naming convention.

    Moves files to:
    - 01_STEMS_MASTER/ (final exports)
    - 02_AUDIO_RAW/ (unprocessed recordings)

    Applies naming: ProjectName_Stage_Version_Type_BPM_Key_Date.wav
    """
```

### 6. Sidechain Automation
```python
@mcp.tool()
async def sidechain_808_to_kick(bass_track: int, kick_track: int,
                                amount_db: float = 4.5) -> str:
    """Apply sidechain compression following folk-hip hop standards.

    Args:
        bass_track: 808 bass track number (typically Track 5)
        kick_track: Kick drum track number
        amount_db: Ducking amount (default 4.5dB, range 3-6dB)
    """
```

### 7. Circuit Rhythm Prep
```python
@mcp.tool()
async def prep_circuit_samples(project_name: str) -> str:
    """Export audio samples optimized for Circuit Rhythm.

    Specifications:
    - Mono WAV 48kHz
    - Max 220 seconds per pack
    - Organized: T1-4 drums, T5 bass, T6-8 melodic

    Returns path to Components-compatible folder structure
    """
```

### 8. Production Metrics Logger
```python
@mcp.tool()
async def log_production_session(duration_min: int, stage: str, notes: str) -> str:
    """Track time spent per production stage for workflow optimization.

    Stages: beat_generation, recording, mixing, export

    Helps validate async workflow targets:
    - Evening: 30min beat generation
    - Morning: 30min review/selection
    - Afternoon: 1-2hr recording
    """
```

## Implementation Priority

### Phase 1 (Immediate Value)
1. **export_dual_output** - Automates most tedious manual task
2. **apply_folk_hiphop_template** - Ensures consistent genre production
3. **sidechain_808_to_kick** - Critical for folk-hip hop sound

### Phase 2 (Workflow Enhancement)
4. **organize_stems** - Maintains file naming convention
5. **verify_freq_space** - Prevents mixing issues before recording
6. **prep_circuit_samples** - Streamlines live performance prep

### Phase 3 (Advanced Automation)
7. **batch_generate_beats** - Full overnight automation
8. **log_production_session** - Data-driven workflow optimization

## Technical Architecture

### Server Structure
```
ableton-mcp-server/
├── ableton_server.py          # Main FastMCP server entry
├── tools/
│   ├── export_tools.py        # Dual output, stem organization
│   ├── mixing_tools.py        # Sidechain, EQ, template application
│   ├── analysis_tools.py      # Frequency verification, metrics
│   └── integration_tools.py   # API batch processing
├── config.json                # Paths, API keys, default values
├── requirements.txt
├── .mcp.json                  # Claude Code/Desktop config
└── tests/
    └── test_tools.py
```

### Configuration Example
```json
{
  "mcpServers": {
    "ableton-grooves": {
      "command": "python",
      "args": ["C:\\path\\to\\ableton_server.py"],
      "env": {
        "ABLETON_LIVE_PATH": "C:\\ProgramData\\Ableton\\Live 12",
        "SOUNDRAW_API_KEY": "${SOUNDRAW_API_KEY}",
        "PROJECT_ROOT": "C:\\Users\\dread\\documents\\claude_grooves"
      }
    }
  }
}
```

## Resources

- **MCP Quickstart**: https://modelcontextprotocol.io/quickstart/server
- **FastMCP Python Framework**: Recommended for async workflows
- **GitHub Examples**: https://github.com/modelcontextprotocol/servers
- **Ableton Python API**: Access via Max for Live or Live Object Model (LOM)

## Integration with Roadmap

Aligns with ROADMAP.md phases:
- **Phase 3 (Month 2)**: AI Tool Integration - Begin with Phase 1 tools
- **Phase 4 (Month 3)**: Custom Automation - Complete all tools, Python scripts
- **Phase 5 (Month 4-6)**: Production Scaling - Use tools for 3-5 track completion

## Success Metrics

- Time saved per track: Target 2-4 hours reduction via automation
- Consistency: 100% adherence to naming convention and dual export format
- Error reduction: Eliminate frequency conflicts, improper sidechain settings
- Workflow validation: Track actual time vs. async workflow targets

---

## Mixer Write Controls: Strategy & Implementation

### Current State vs. Vision

**Current (Read-Only)**: MCP can query mixer state, BPM, track info, but cannot modify settings

**Target (Write Access)**: Full mixer automation with safeguards for template application, batch operations, and async workflow integration

### Strategic Value of Write Controls

#### High-Impact Benefits
1. **Template Automation** - One command sets up guitar HPF, 808 sidechain, reverb routing across all tracks
2. **Consistent Mixing** - Folk-hip hop frequency management applied perfectly every time
3. **Iteration Speed** - Claude adjusts EQ/compression based on frequency analysis, user reviews results
4. **Batch Operations** - "Apply 3dB ducking to all 808 tracks" instead of manual clicking

#### Async Workflow Multiplier
- **Morning review session**: "Claude, prep yesterday's beat with the folk-hip hop template"
- **Mixing phase**: "Boost guitar presence, check for bass conflicts, apply standard sidechain"
- **Pre-export**: "Verify all tracks meet -10 LUFS target, adjust levels"

### Risk Assessment & Mitigation

#### Real Risks
1. **Accidental Destruction** - Wrong track number could mute lead vocal
2. **No Native Undo** - Changes happen in Ableton, MCP doesn't track history
3. **Trust Barrier** - Takes time to feel comfortable with AI adjusting mix
4. **Cascading Errors** - One bad EQ setting could require full mix revision

#### Mitigation Strategy
- **Default to dry-run mode** - Force explicit confirmation for changes
- **Always snapshot first** - Auto-save mixer state before writes
- **Limit blast radius** - Single track operations before multi-track
- **Log everything** - Track what changed, when, and why
- **Progressive trust** - Build confidence with safe operations first

### Phased Implementation Approach

#### Tier 1: Safe, Non-Destructive (Start Here)
```python
@mcp.tool()
async def solo_track(track: int) -> str:
    """Solo a track for review."""

@mcp.tool()
async def add_return_send(track: int, return_name: str, amount: float) -> str:
    """Add reverb/delay send (doesn't change existing mix)."""

@mcp.tool()
async def create_mix_snapshot(name: str) -> str:
    """Save current mixer state before changes."""

@mcp.tool()
async def restore_snapshot(snapshot_id: str) -> str:
    """Revert to previous mixer state."""
```

**Timeline**: Month 2 (Phase 3)
**Goal**: Build snapshot/restore functionality, test with non-critical projects

#### Tier 2: Controlled Adjustments (With Safeguards)
```python
@mcp.tool()
async def adjust_track_volume(track: int, change_db: float,
                              dry_run: bool = True) -> str:
    """Adjust volume with preview mode.

    Args:
        track: Track number (1-indexed)
        change_db: Decibel adjustment (positive or negative)
        dry_run: If True, only reports what would change (no action)

    Returns:
        Preview or confirmation message
    """
    if dry_run:
        current_vol = get_track_volume(track)
        new_vol = current_vol + change_db
        return f"Preview: Track {track} would change from {current_vol}dB to {new_vol}dB"

    # Actual change with snapshot
    snapshot_id = await create_mix_snapshot(f"auto_before_vol_change")
    try:
        result = set_track_volume(track, change_db)
        return f"Success: {result}\nSnapshot: {snapshot_id}"
    except Exception as e:
        await restore_snapshot(snapshot_id)
        return f"Error: {e}\nReverted to snapshot {snapshot_id}"

@mcp.tool()
async def apply_highpass_filter(track: int, freq_hz: int, dry_run: bool = True) -> str:
    """Apply HPF to acoustic guitar (typically 80-100Hz)."""

@mcp.tool()
async def set_sidechain_amount(bass_track: int, kick_track: int,
                               amount_db: float, dry_run: bool = True) -> str:
    """Adjust sidechain compression (3-6dB range for folk-hip hop)."""
```

**Timeline**: Month 3 (Phase 4)
**Goal**: Add controlled adjustments (volume, pan, simple EQ), implement dry-run mode

#### Tier 3: Template Operations (Confirm Before Apply)
```python
@mcp.tool()
async def apply_folk_hiphop_template(guitar_track: int, bass_track: int,
                                    kick_track: int, confirm: bool = False) -> str:
    """Apply full mixing template for folk-hip hop production.

    REQUIRES confirm=True to execute. Otherwise returns preview.

    Operations:
    1. Guitar: HPF @80Hz, boost +3dB @4kHz
    2. 808 bass: Sidechain to kick (-4.5dB ducking)
    3. Electronic elements: Room reverb 1.2s decay
    4. All tracks: Matching reverb for cohesion

    Args:
        guitar_track: Acoustic guitar track number
        bass_track: 808 bass track number
        kick_track: Kick drum track number
        confirm: Must be True to execute (prevents accidental application)
    """
    changes = [
        f"Guitar HPF @80Hz on Track {guitar_track}",
        f"Guitar boost +3dB @4kHz on Track {guitar_track}",
        f"808 sidechain -4.5dB on Track {bass_track} (source: Track {kick_track})",
        "Room reverb 1.2s decay to all electronic tracks",
        "Verify frequency space (guitar vs 808 bass)"
    ]

    if not confirm:
        return "PREVIEW MODE - Set confirm=True to apply:\n" + "\n".join(changes)

    # Create snapshot before applying
    snapshot_id = await create_mix_snapshot(f"before_template_{timestamp}")

    try:
        # Execute each operation
        await apply_highpass_filter(guitar_track, 80, dry_run=False)
        await apply_eq_boost(guitar_track, freq_hz=4000, gain_db=3, dry_run=False)
        await set_sidechain_amount(bass_track, kick_track, 4.5, dry_run=False)
        await apply_room_reverb_to_electronic_tracks(decay_sec=1.2)

        # Verify results
        freq_check = await verify_freq_space(guitar_track, bass_track)

        return f"Template applied successfully\nSnapshot: {snapshot_id}\nFreq check: {freq_check}"

    except Exception as e:
        await restore_snapshot(snapshot_id)
        return f"Template application failed: {e}\nReverted to snapshot {snapshot_id}"

@mcp.tool()
async def batch_adjust_volumes(track_list: list[int], change_db: float,
                               confirm: bool = False) -> str:
    """Adjust multiple tracks simultaneously (e.g., all drum tracks)."""
```

**Timeline**: Month 4+ (Phase 5)
**Goal**: Full template automation, batch operations across multiple tracks

#### Ultimate Workflow Tool (The Vision)
```python
@mcp.tool()
async def evening_beat_prep(beat_file: str, project_name: str,
                           guitar_track: int = 1, bass_track: int = 5,
                           kick_track: int = 2) -> str:
    """Full automation for morning review session.

    Overnight workflow:
    1. Import beat from overnight generation
    2. Apply folk-hip hop template
    3. Verify frequency space for guitar (80-100Hz clear)
    4. Set up sidechain routing
    5. Create README with BPM, key, plugins used
    6. Save snapshot for recording session

    Result: Wake up to a mix-ready project

    Args:
        beat_file: Path to generated beat WAV/MIDI
        project_name: Track name for file organization
        guitar_track: Reserved track for acoustic guitar (default 1)
        bass_track: 808 bass track (default 5)
        kick_track: Kick drum track (default 2)

    Returns:
        Summary of operations and paths to created files
    """
    log = []

    # Import beat
    import_result = await import_audio_to_tracks(beat_file)
    log.append(f"Imported: {import_result}")

    # Apply template
    template_result = await apply_folk_hiphop_template(
        guitar_track, bass_track, kick_track, confirm=True
    )
    log.append(f"Template: {template_result}")

    # Frequency verification
    freq_check = await verify_freq_space(guitar_track, bass_track)
    log.append(f"Freq space: {freq_check}")

    # Create README
    bpm = await get_project_bpm()
    key = await detect_musical_key()
    readme_path = await create_project_readme(project_name, bpm, key)
    log.append(f"README: {readme_path}")

    # Save snapshot
    snapshot_id = await create_mix_snapshot(f"{project_name}_ready_for_recording")
    log.append(f"Snapshot: {snapshot_id}")

    return "\n".join(log)
```

**Timeline**: Month 6+ (Phase 6 - Long-term optimization)
**Goal**: Async workflow multiplier - AI handles mechanical setup overnight

### Implementation Principles

1. **Default to dry-run mode** - All write operations preview by default
2. **Always snapshot first** - Auto-save mixer state before any changes
3. **Limit blast radius** - Start with single track operations before multi-track batch
4. **Log everything** - Track what changed, when, and why for accountability
5. **Progressive trust** - Build confidence with safe operations before destructive ones

### Critical Safeguard Pattern

All write operations should follow this pattern:

```python
async def safe_mix_operation(operation: callable, operation_name: str) -> str:
    """Wrapper that auto-saves before any write operation.

    Args:
        operation: The mixing function to execute
        operation_name: Human-readable name for logging

    Returns:
        Success/failure message with snapshot ID
    """
    # Create timestamped snapshot
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    snapshot_id = await create_mix_snapshot(f"auto_{operation_name}_{timestamp}")

    # Log operation start
    logging.info(f"Starting operation: {operation_name}")
    logging.info(f"Snapshot created: {snapshot_id}")

    try:
        # Execute operation
        result = await operation()

        # Log success
        logging.info(f"Operation succeeded: {operation_name}")
        logging.info(f"Result: {result}")

        return f"Success: {result}\nSnapshot: {snapshot_id}"

    except Exception as e:
        # Log failure
        logging.error(f"Operation failed: {operation_name}")
        logging.error(f"Error: {e}")

        # Automatic rollback
        await restore_snapshot(snapshot_id)
        logging.info(f"Reverted to snapshot: {snapshot_id}")

        return f"Error: {e}\nReverted to snapshot {snapshot_id}"
```

### Recommended Rollout Timeline

**Month 2 (Phase 3 - AI Tool Integration)**
- Implement Tier 1 safe operations (solo, mute, sends)
- Build snapshot/restore system
- Test with non-critical projects

**Month 3 (Phase 4 - Custom Automation)**
- Add Tier 2 controlled adjustments (volume, pan, EQ)
- Implement dry-run mode for all operations
- Build folk-hip hop template tool
- Validate with 1-2 complete tracks

**Month 4-6 (Phase 5 - Production Scaling)**
- Tier 3 full template automation
- Batch operations across multiple tracks
- Advanced sidechain/dynamics processing
- Use for 3-5 track completion

**Month 6+ (Phase 6 - Long-Term Optimization)**
- Ultimate workflow tool: `evening_beat_prep()`
- Full overnight automation pipeline
- Advanced features based on usage data

### Success Criteria

- **Trust established**: Comfortable using template automation without manual verification
- **Time savings**: 2-4 hours per track via automated mixing setup
- **Zero data loss**: Snapshot system prevents any accidental destruction
- **Consistency**: 100% adherence to folk-hip hop mixing standards
- **Workflow validation**: Morning sessions start with mix-ready projects

---

## Next Steps

1. **Review existing Ableton MCP server** - Understand current read-only capabilities
2. **Set up development environment** - Python, FastMCP, Ableton Live API access
3. **Implement Tier 1 tools** - Safe operations + snapshot system
4. **Test with non-critical project** - Validate safety mechanisms
5. **Iterate based on real-world usage** - Adjust tooling to actual workflow needs
