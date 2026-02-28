# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Claude Grooves** is an asynchronous AI-human music production project for folk-hip hop. The core philosophy: production happens in DAW with AI assistance; performance happens with Circuit Rhythm. Claude acts as creative director, prompt engineer, and workflow orchestrator.

## Architecture

### Workflow Pattern: Async Production Cycle
```
Evening (30m):   AI beat generation via Claude + MCP or API batch processing
Morning (30m):   Review/selection of generated beats
Afternoon (1-2h): Recording (acoustic guitar or vocals)
Following days:  Mixing → dual export (streaming + live backing track)
```

### Tool Stack
- **DAW**: Ableton Live 12 (recommended for MCP integration)
- **AI Integration**: Claude Desktop + Ableton MCP for direct DAW control
- **Beat Generation**: Soundraw (MIDI export), MusicAPI.ai, or Emergent Drums 2 VST
- **Hardware**: Novation Circuit Rhythm (live performance only, NOT studio production)
- **Automation**: Python scripts for batch API processing

### File Organization Convention

```
ProjectName_Stage_Version_Type_BPM_Key_Date.wav
Example: Nightfall_MIX_v3_INST_088_Em_20251115.wav

Project_Root/
├── 01_STEMS_MASTER/     # Final exported stems
├── 02_AUDIO_RAW/        # Unprocessed recordings
├── 03_PROJECT_FILES/    # DAW project files
├── 04_NOTES_DOCS/       # README.txt with BPM, key, plugins, collaborators
└── 05_REFERENCES/       # Reference tracks and inspirations
```

### Dual Output Strategy
1. **Studio Mix**: Streaming platforms (-10 LUFS, -1.5 dBTP, WAV 24-bit/48kHz)
2. **Live Backing Track**: Circuit Rhythm samples (mono WAV 48kHz, max 220s per Pack)

## Working with Circuit Rhythm

**Critical**: Circuit Rhythm has NO USB audio streaming and NO MIDI file import. Do not attempt to integrate it into studio production workflow.

**Correct usage**:
- Produce entirely in DAW with AI assistance
- Export finished beat stems as audio samples
- Load samples via Novation Components software
- Manually program patterns for live performance
- Tracks 1-4: drums/percussion | Track 5: bass | Tracks 6-8: melodic/texture

## Python Automation Scripts

When writing automation scripts for this project:
- **Batch beat generation**: Submit multiple API requests overnight (Soundraw, MusicAPI.ai)
- **File organization**: Auto-rename and organize exported stems per naming convention
- **Metadata management**: Extract BPM, key, duration from audio files
- **Backup verification**: Ensure 3-2-1 backup rule (local + external + cloud)

## Genre-Specific Production Rules

**Folk-Hip Hop Frequency Management**:
- High-pass acoustic guitar at 80-100 Hz (avoid 808 bass clash)
- Boost guitar at 3-5 kHz for presence
- Sidechain 808 bass to kick (3-6 dB ducking, essential)
- Add matching room reverb (0.5-1.5s decay) to ALL electronic elements

**Arrangement Hierarchy**:
- If guitar is rhythmic → keep drums simple
- If drums are complex → keep guitar sustained/melodic
- Poor arrangement cannot be fixed in mixing

**Tempo Range**: 80-95 BPM sweet spot

## API Cost Optimization

- **Prompt caching**: 90% cost savings on repeated content
- **Batch processing**: 50% discount for non-urgent workloads
- **Model selection**: Haiku for simple tasks, Sonnet for creative direction
- **Target costs**: Light use $15-25/month, moderate $40-60/month

## Current Phase

Reference ROADMAP.md for implementation phases. Project follows 6-phase roadmap:
1. Foundation (Weeks 1-2): Setup, first test
2. Workflow Refinement (Weeks 3-4): Establish async routine
3. AI Tool Integration (Month 2): Expand capabilities
4. Custom Automation (Month 3): Python scripts, optional MCP experimentation
5. Production Scaling (Months 4-6): Complete 3-5 tracks, live integration
6. Long-Term Optimization (Month 6+): Advanced features if justified

## Deferred Items (6-12 months)

Do NOT pursue:
- Real-time live AI performance integration
- Custom MCP Circuit Rhythm development (unless Phase 4 POC succeeds)
- GPU investment (not needed for async workflow)
- Advanced MCP features (wait for ecosystem maturity Q1-Q4 2026)

## When Assisting with This Project

1. **Beat generation prompts**: Craft detailed prompts for AI tools including BPM, key, mood, frequency space for acoustic guitar, reference artists
2. **File naming**: Always follow the convention: `ProjectName_Stage_Version_Type_BPM_Key_Date`
3. **Circuit Rhythm advice**: Remind user of limitations; guide toward DAW production + live performance separation
4. **Python scripting**: Leverage user's IT skills for workflow automation
5. **Cost awareness**: Track and optimize API usage; recommend caching and batching

## Success Metrics

- Month 1: 1 complete track, async workflow established
- Month 3: 3-5 tracks, Python automation functional
- Month 6: 5-10 tracks, live rig tested, revenue generating
