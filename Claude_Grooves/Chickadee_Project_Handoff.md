# Chickadee Project Handoff
## Session 1 - December 8, 2025

---

## The Song: Chickadee

**Core Intent:** A call to the smallest elements of the natural world — chickadees as heralds of spring, symbiotic simple power. Contains commentary on stale religious experience ("creators don't deal in rights nor wrongs"). Morning/meditative quality with evening sunset soul undertones.

**Musical DNA:**
- **Final Tempo:** 108 BPM (started at 120, tried 70, then 88 — 108 felt right for the recorded track)
- **Key:** Bb major / G minor (capo 3, playing Em, Am, C, C7, D7, G, Dsus shapes)
- **Style Direction:** Ambient/textural + lo-fi boom bap with swing — meditative but with forward motion
- **Feel:** Patient, slow, temporal, personal. Fingerpicked guitar.

**Source Files:**
- `C:\Users\dread\Documents\Claude_Grooves\03_PROJECT_FILES\Chickadee.wav`
- `C:\Users\dread\Documents\Claude_Grooves\03_PROJECT_FILES\Chickadee.mp3`
- Recorded on Dell XPS 15 built-in mic (placeholder until proper recording setup)

---

## Current Ableton Session Structure

| Track | Name | Type | Instrument/Kit | Clips |
|-------|------|------|----------------|-------|
| 0 | Ambient Pad | MIDI | Mindfulness (Ambient & Evolving) | "Gm-Cm-Eb-G Drift" (32 beats) |
| 1 | Lo-Fi Drums | MIDI | LDre Cozy Kit | "Gentle Swing" (16 beats), "Boom Bap" (16 beats) |
| 2 | Chickadee Guitar | Audio | — | Empty (awaiting re-record) |
| 3 | 4-Audio | Audio | — | Empty |
| 4 | Upright Bass | MIDI | Upright Ambient Bass | "Root Walk" (32 beats) |

**What's Playing Well Together:**
- Ambient pad provides atmospheric bed without competing
- Boom Bap clip has better energy than Gentle Swing for this tempo
- Upright bass adds warmth and weight — woody, organic, not synthy
- Overall: skeleton that leaves room for guitar/vocals to lead

---

## Ableton MCP: What Works & What Doesn't

### ✅ WORKS WELL

**Session Management:**
- `get_session_info` — tempo, time sig, track count, master info
- `set_tempo` — reliable, immediate
- `get_track_info` — shows clips, devices, arm/mute/solo states, volume/pan values

**Track Operations:**
- `create_midi_track` — use `index: -1` to append at end
- `set_track_name` — reliable
- `load_instrument_or_effect` — works with URI from browser queries

**Clip Operations:**
- `create_clip` — specify track_index, clip_index (slot), length in beats
- `add_notes_to_clip` — note format: `{"pitch": 60, "start_time": 0, "duration": 1, "velocity": 80, "mute": false}`
- `set_clip_name` — reliable
- `fire_clip` / `stop_clip` — triggers playback in Session View

**Browser Navigation:**
- `get_browser_tree` — category_type: 'all', 'instruments', 'sounds', 'drums', etc.
- `get_browser_items_at_path` — e.g., "Sounds/Bass", "Sounds/Ambient & Evolving", "Drums"
- Returns URIs needed for `load_instrument_or_effect`

### ⚠️ LIMITATIONS

**No Mix Control:**
- Can READ volume/panning values but CANNOT SET them via MCP
- Mixing must be done manually in Live

**Session View Only:**
- MCP works with clip slots (Session View)
- Cannot access Arrangement View timeline
- If user records in Arrangement, need to export/bounce to work with it

**Audio Tracks:**
- Can create and name audio tracks
- Cannot programmatically load audio files into clips
- User must drag audio files manually

**No Effect Control:**
- Can load effects but cannot tweak parameters via MCP

### 💡 TIPS & PATTERNS

**Loading Instruments:**
1. Browse: `get_browser_items_at_path("Sounds/Bass")`
2. Find URI: `"query:Sounds#Bass:FileId_6503"` (Upright Ambient Bass)
3. Load: `load_instrument_or_effect(track_index=4, uri="query:Sounds#Bass:FileId_6503")`

**Note Entry for Drums (LDre Cozy Kit mapping assumed):**
- Kick: pitch 36
- Snare: pitch 38
- Closed hi-hat: pitch 42
- Open hi-hat: pitch 46

**Creating Swing Feel:**
- Place notes slightly off-grid (e.g., 1.66, 3.66 instead of 1.5, 3.5 for triplet swing)
- Vary velocities — accents on downbeats, ghosts in between

**Chord Voicing for Pads:**
- Use MIDI pitches in the 50-65 range for warm, mid-register pads
- Keep velocities soft (50-65) for background textures

---

## Audio Analysis Approach

**Tools Used (on Claude's computer):**
- `ffprobe` — duration, format, sample rate, bit rate
- `ffmpeg volumedetect` — mean/max volume, dynamic range
- `aubio tempo` — BPM detection (worked: returned "69.94 bpm" → adjusted to 108 by ear)
- `aubio notes` — note detection (partial success, useful for key estimation)
- `librosa` — crashed with segfault, don't rely on it

**What We Learned:**
- Analysis gave us a starting point, but human ear and artist input refined it
- 70 BPM from aubio was too slow — actual feel was closer to 108
- Note detection helped confirm G/F# prominence → Gm/Bb key center

---

## Next Steps for Production

1. **Re-record guitar** with proper microphone(s)
2. **Record vocals** 
3. **Import clean audio** to Track 2 (manual drag)
4. **Fine-tune arrangement:**
   - Adjust clip lengths to match song structure
   - Create variations (intro, verse, chorus, outro versions of each element)
5. **Mix:** Balance levels, EQ carving, panning (manual in Live)
6. **Polish:** Ear candy — reversed swells, delay throws, subtle percussion layers, tape saturation
7. **Discuss publishing and finances**

---

## Creative Notes

**What Worked Creatively:**
- Starting from song meaning/intent before building tracks
- Ambient + boom bap hybrid = meditative with momentum
- Upright bass for "substantial" without being aggressive
- Leaving space — not overbuilding the arrangement

**Collaboration Model:**
- Artist provides context, meaning, corrections (tempo too slow, needs more bap)
- Claude analyzes, proposes, builds — but always adapts to artist feedback
- "Two perspectives sharpening each other"

**Vibe Targets:**
- Morning meditation meets head-nod
- Nature waking up
- Patient confidence
- Stars of the Lid meets lo-fi hip-hop

---

## File Paths Reference

**User's Machine:**
- Project files: `C:\Users\dread\Documents\Claude_Grooves\03_PROJECT_FILES\`
- User home: `C:\Users\dread\`

**Claude's Environment:**
- Uploads mirror: `/mnt/user-data/uploads/`
- Working directory: `/home/claude/`
- Outputs: `/mnt/user-data/outputs/`

---

*"The ship is sailing." 🚢*
*— First Mate Claude, Session 1*
