# Strudel MCP Integration with Claude Grooves

## Overview

Strudel is a live-coding music environment that generates patterns algorithmically. This document describes how to integrate Strudel-generated patterns into the Claude Grooves production workflow.

## Why Strudel + Ableton?

| Strudel Strengths | Ableton Strengths |
|-------------------|-------------------|
| Algorithmic pattern generation | Arrangement and mixing |
| Real-time pattern transformation | Acoustic recording |
| Mathematical precision | Plugin ecosystem |
| Generative exploration | Export and distribution |

**The Bridge**: Use Strudel for beat ideation and pattern generation, then import to Ableton for production, recording, and mixing.

## Workflow Integration

### Evening: Strudel Pattern Generation

1. **Launch Strudel MCP** via Claude Desktop:
   ```bash
   claude mcp add strudel node path/to/strudel-mcp-server/dist/index.js
   ```

2. **Generate patterns** with genre-specific prompts:
   ```
   "Create a folk-hip hop pattern at 88 BPM in Em with space for acoustic guitar"
   ```

3. **Iterate with transformations**:
   - `.fast(2)` - double speed
   - `.slow(2)` - half speed
   - `.rev` - reverse pattern
   - `.every(4, x => x.fast(2))` - variation every 4 cycles

4. **Save promising patterns** with tags:
   ```
   save name="evening-groove-1" tags="folk-hiphop,88bpm,em"
   ```

### Morning: Pattern Review

1. **List saved patterns**:
   ```
   list tags="folk-hiphop"
   ```

2. **Load and audition** top candidates:
   ```
   load name="evening-groove-1"
   play
   ```

3. **Export for Ableton** (see Export Methods below)

### Afternoon: Ableton Production

1. Import exported MIDI/audio to Ableton
2. Record acoustic guitar over beat
3. Record vocals
4. Mix with Ableton MCP assistance

## Export Methods

### Method 1: Audio Recording (Recommended for Now)

1. Play pattern in Strudel browser
2. Use system audio routing (e.g., VB-Cable, BlackHole) to capture
3. Record into Ableton as audio track
4. Slice/arrange as needed

**Pros**: Captures exact sound including Strudel's built-in synthesis
**Cons**: Not editable as MIDI

### Method 2: Pattern Transcription

1. View pattern code in Strudel
2. Manually transcribe rhythm to Ableton MIDI clip
3. Apply similar instruments/effects

**Example Transcription**:
```
Strudel: s("bd ~ cp ~, hh*8")
Ableton:
  - Track 1 (Kick): Notes at 1.1, 3.1
  - Track 2 (Clap): Notes at 2.1, 4.1
  - Track 3 (HiHat): 8 evenly-spaced notes
```

### Method 3: MIDI File Export (Future)

Strudel supports MIDI output in some configurations. When available:
1. Configure Strudel MIDI output
2. Route to Ableton via virtual MIDI port
3. Record as MIDI clip

## Genre Integration: Folk-Hip Hop

The folk-hip hop patterns in `patterns/examples/folk-hiphop/` are designed for this workflow:

### organic-minimal.json
- **BPM**: 88
- **Key**: Em
- **Character**: Sparse, warm, Atmosphere-inspired
- **Guitar space**: 250-500 Hz deliberately empty
- **Best for**: Fingerpicking accompaniment, storytelling tracks

### storyteller.json
- **BPM**: 85
- **Key**: Am
- **Character**: Maximum vocal space, near-minimal
- **Guitar space**: Entire mid-range open
- **Best for**: Spoken word, lyric-heavy delivery

### folk-roots.json
- **BPM**: 92
- **Key**: Dm
- **Character**: Shuffle groove, bluesy warmth
- **Guitar space**: Designed for fingerpicking
- **Best for**: Delta blues fusion, folk melodies

## Frequency Considerations

When importing Strudel patterns to Ableton for folk-hip hop:

1. **HPF acoustic guitar** at 80-100 Hz (avoid 808 clash)
2. **Check 250-500 Hz** - patterns are designed to leave this space open
3. **Match reverb** - add room reverb to Strudel elements to match guitar's natural room

## Pattern Transformation for Variation

In Strudel, create variations before export:

```javascript
// Original
s("bd ~ cp ~")

// Variation 1: Busier
s("bd ~ cp ~").fast(2)

// Variation 2: Every 4th bar different
s("bd ~ cp ~").every(4, x => x.fast(2))

// Variation 3: Sometimes reverse
s("bd ~ cp ~").sometimes(x => x.rev)

// Variation 4: Humanize timing
s("bd ~ cp ~").swing(0.12)
```

Export multiple variations for verse/chorus/bridge in Ableton.

## Tool Comparison

| Task | Use Strudel | Use Ableton MCP |
|------|-------------|-----------------|
| Pattern ideation | Yes | No |
| Algorithmic generation | Yes | No |
| Pattern transformation | Yes | Limited |
| Recording audio | No | Yes |
| Mixing | No | Yes |
| Effects automation | Limited | Yes |
| Export/render | Limited | Yes |
| Live performance | Possible | Limited |

## Future Integration Ideas

1. **Direct MIDI routing**: Strudel → Virtual MIDI → Ableton Live
2. **Hybrid MCP session**: Both Strudel MCP and Ableton MCP active
3. **Pattern memory**: Query Rhiz memory for "patterns that worked well with acoustic guitar"
4. **Mathematical similarity**: "Find patterns with similar density to evening-groove-1"

## Quick Reference

### Strudel Folk-Hip Hop Prompt Template
```
Create a folk-hip hop pattern at [BPM] BPM in [KEY] with:
- Sparse drums (kick and snare only on downbeats)
- Sub bass in the 80-150 Hz range
- Swing of 0.12 for lazy groove
- Room reverb on electronic elements
- Leave 250-500 Hz clear for acoustic guitar
```

### Common BPM/Key Combinations
- 85 Am - Sage Francis storyteller territory
- 88 Em - Atmosphere organic warmth
- 92 Dm - Delta blues feel
- 95 Gm - Modern folk-hop

---

*Part of Claude Grooves async production workflow*
*Integration designed for folk-hip hop genre*
