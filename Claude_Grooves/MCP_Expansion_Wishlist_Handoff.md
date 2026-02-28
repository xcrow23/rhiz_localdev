# MCP Expansion Wishlist - Handoff to Claude Code
## Session: December 13, 2025

---

## Executive Summary

Through extensive testing of the Ableton MCP (uisato/ableton-mcp-extended) across 5+ complete track productions, we've identified critical gaps between current capabilities and production workflow needs. This document provides a prioritized wishlist for MCP expansion, focusing on folk-hip hop async production workflow requirements.

**Testing Methodology**: Created 5 complete tracks spanning multiple genres (Australian hip-hop, reggae fusion, rock hip-hop, hand drum polyrhythms) pushing MCP's limits on clip complexity, multi-scene arrangements, and polyrhythmic layering.

**Bottom Line**: MCP excels at MIDI clip creation and track organization, but lacks mixer control, effect automation, and export capabilities needed for complete production workflow.

---

## Current MCP Capabilities (What Works ✅)

### Track Management
- `create_midi_track(index)` - Works flawlessly
- `set_track_name(track_index, name)` - Essential, reliable
- `get_track_info(track_index)` - Good visibility into track state

### Instrument Loading
- `load_instrument_or_effect(track_index, uri)` - Browser URIs work great
- `get_browser_tree(category_type)` - Effective navigation
- `get_browser_items_at_path(path)` - Returns loadable URIs

### MIDI Clip Creation
- `create_clip(track_index, clip_index, length)` - Solid foundation
- `add_notes_to_clip(track_index, clip_index, notes)` - Handles complex patterns
- `set_clip_name(track_index, clip_index, name)` - Critical for organization
- Successfully tested with 30+ note patterns, varied velocities, polyrhythmic structures

### Transport & Session
- `start_playback()` / `stop_playback()` - Reliable
- `set_tempo(bpm)` - Works (network permitting)
- `get_session_info()` - Useful project state visibility
- `fire_clip(track_index, clip_index)` / `stop_clip()` - Session View control

---

## Critical Missing Features (Priority Order)

### **PRIORITY 1: MIXER WRITE CONTROLS** 🔴

Current state: **READ-ONLY** - Can query volume/pan but cannot set them.

#### Core Mixer Tools
```python
set_track_volume(track_index: int, db: float) -> str
    """Set track volume in decibels.
    
    Args:
        track_index: Track number (0-indexed)
        db: Volume in dB (-inf to +6.0, typical range -20 to 0)
    
    Returns:
        Confirmation message
    """

set_track_pan(track_index: int, position: float) -> str
    """Set track stereo panning.
    
    Args:
        track_index: Track number
        position: Pan position (-1.0 = hard left, 0.0 = center, 1.0 = hard right)
    
    Returns:
        Confirmation message
    """

set_track_mute(track_index: int, mute: bool) -> str
    """Mute or unmute a track.
    
    Args:
        track_index: Track number
        mute: True to mute, False to unmute
    """

set_track_solo(track_index: int, solo: bool) -> str
    """Solo or unsolo a track."""

set_send_amount(track_index: int, return_index: int, amount: float) -> str
    """Set send level to return track (reverb/delay).
    
    Args:
        track_index: Source track
        return_index: Return track (0 = A, 1 = B, etc.)
        amount: Send amount (0.0 to 1.0)
    
    Returns:
        Confirmation message
    """
```

#### Sidechain & Ducking Tools
```python
set_sidechain_compressor(
    target_track: int,
    source_track: int,
    threshold_db: float = -20.0,
    ratio: float = 4.0,
    attack_ms: float = 3.0,
    release_ms: float = 50.0,
    amount_db: float = 6.0
) -> str
    """Apply sidechain compression (essential for folk-hip hop 808/kick interaction).
    
    Args:
        target_track: Track to compress (e.g., bass)
        source_track: Trigger track (e.g., kick)
        threshold_db: Compression threshold
        ratio: Compression ratio (4:1 recommended)
        attack_ms: How quickly compression engages
        release_ms: How quickly compression releases
        amount_db: Amount of ducking (3-6 dB typical)
    
    Returns:
        Confirmation with settings applied
    
    Example:
        # Duck 808 bass to kick
        set_sidechain_compressor(
            target_track=5,  # Bass
            source_track=2,  # Kick
            amount_db=4.5
        )
    """

enable_auto_ducking(vocal_track: int, music_tracks: list[int], amount_db: float = 3.0) -> str
    """Automatically duck music when vocals are present.
    
    Args:
        vocal_track: Track triggering ducking
        music_tracks: List of tracks to duck
        amount_db: Ducking amount (2-4 dB typical)
    """
```

#### Grid FX & Performance Tools
```python
set_track_grid_fx(
    track_index: int,
    fx_type: str,
    parameters: dict
) -> str
    """Apply Grid FX (Circuit Rhythm-style live performance effects).
    
    Args:
        track_index: Track to apply FX
        fx_type: Effect type - options:
            - "beat_repeat": Stutter/repeat patterns
            - "reverser": Reverse playback
            - "filter": Resonant filter sweep
            - "delay_throw": Delay feedback buildup
            - "bit_crusher": Lo-fi degradation
            - "tape_stop": Tape slow-down effect
        parameters: Effect-specific settings
    
    Returns:
        Confirmation message
    
    Examples:
        # Beat repeat on drums
        set_track_grid_fx(
            track_index=1,
            fx_type="beat_repeat",
            parameters={
                "interval": "1/8",  # Repeat every 8th note
                "gate": 4,          # Number of repeats
                "mix": 0.3          # Effect blend
            }
        )
        
        # Filter sweep on synth
        set_track_grid_fx(
            track_index=6,
            fx_type="filter",
            parameters={
                "cutoff_start": 200,   # Hz
                "cutoff_end": 8000,    # Hz
                "resonance": 0.7,
                "duration": 4.0        # Beats
            }
        )
```

#### Use Case: Folk-Hip Hop Template
```python
def apply_folk_hiphop_mixing_template(
    guitar_track: int,
    bass_track: int,
    kick_track: int,
    electronic_tracks: list[int]
):
    """One-command mixing setup for folk-hip hop production."""
    
    # Guitar: HPF 80Hz, presence boost, slight pan
    set_highpass_filter(guitar_track, freq_hz=80)
    set_eq_boost(guitar_track, freq_hz=4000, gain_db=3)
    set_track_pan(guitar_track, 0.25)
    
    # 808 bass: Sidechain to kick (essential!)
    set_sidechain_compressor(
        target_track=bass_track,
        source_track=kick_track,
        amount_db=4.5
    )
    
    # Electronic elements: Matching room reverb (cohesion)
    for track in electronic_tracks:
        set_send_amount(track, return_index=0, amount=0.15)
    
    # Set reverb to 1.2s decay
    set_reverb_decay(return_track=0, decay_sec=1.2)
```

**Impact Without These Tools**: 
- Cannot implement genre-specific mixing techniques
- Cannot balance tracks programmatically
- Manual mixing required after every AI generation session
- Breaks async workflow (evening generation → morning review with proper mix)

---

### Additional Priority Tools

*See full document for:*
- **Priority 2**: Effect Parameter Control
- **Priority 3**: Scene Management
- **Priority 4**: Audio File Import
- **Priority 5**: Batch Operations
- **Priority 6**: Export Capabilities
- **Priority 7**: Arrangement View Access

---

## Implementation Priority Summary

### Phase 1 (Critical - Unblocks Production Workflow)
1. ✅ **Mixer Write Controls** - Volume, pan, sends, mute/solo
2. ✅ **Sidechain/Ducking** - Essential for folk-hip hop genre
3. ✅ **Grid FX** - Live performance capabilities
4. ✅ **Basic Effect Parameters** - EQ, compression, reverb/delay

### Phase 2 (High Value - Automation & Organization)
5. ✅ **Scene Management** - Song structure creation
6. ✅ **Audio Import** - Load recordings and AI beats
7. ✅ **MIDI Export** - Complete async workflow loop

### Phase 3 (Efficiency & Advanced Features)
8. ✅ **Batch Operations** - Cleaner code, faster execution
9. ✅ **Stem Export** - Circuit Rhythm workflow
10. ✅ **Arrangement View** - Linear song creation

### Phase 4 (Power User Features)
11. ✅ **Master Render** - Complete bounce automation
12. ✅ **Dual Export** - One-command streaming + live
13. ✅ **Template System** - Genre-specific presets

---

## Testing Evidence

**What We Built Today (12/13/2025)**:
1. ✅ Australian Hip Hop fusion (92 BPM) - Dense arrangement, jazzy samples
2. ✅ Reggae Hip Hop (88 BPM) - Offbeat skank, brass stabs
3. ✅ Rock Hip Hop (136 BPM) - Syncopated rhythm guitars, scarecrow walk
4. ✅ Hand Drum Polyrhythms (112 BPM) - West African + Indian + Afro-Cuban + evolving frame drum (4 layers!)
5. ✅ Circuit Echo foundation (108 BPM) - Multi-scene structure testing

**What Worked**: MIDI clip creation, complex note patterns, instrument loading, track naming, transport control

**What We Missed**: Volume balancing, frequency management, sidechain compression, reverb sends, MIDI export, stem export, scene launching

---

## Success Metrics

### Developer Experience
- ✅ Reduce code verbosity by 50%+ (batch operations)
- ✅ Enable complete workflow automation (generation → mixing → export)
- ✅ Eliminate manual export steps (MIDI, stems, master)

### Production Workflow
- ✅ Evening: Submit beat generation job
- ✅ Overnight: AI generates + MCP applies mixing template
- ✅ Morning: Review mix-ready beats + Circuit Rhythm packs
- ✅ Afternoon: Record guitar/vocals over selected beat
- ✅ Following day: Export streaming master

---

## Contact & Context

**Project**: Claude Grooves - Async AI-Human Folk-Hip Hop Production  
**Primary User**: dread (IT professional, acoustic guitarist, async workflow)  
**DAW**: Ableton Live 12  
**Current MCP**: uisato/ableton-mcp-extended (57 commits, 91 stars)  
**Testing Date**: December 13, 2025  
**Session Output**: 5 complete tracks demonstrating current MCP limits

**Key Insight**: MCP excels at creation but lacks the mixing/export layer needed for production-ready output. Adding mixer controls, grid FX, ducking, and export capabilities transforms it from "beat sketcher" to "complete production tool."

---

*"The grooves are within reach. Let's give MCP the tools to polish them." ⚓🎵*
