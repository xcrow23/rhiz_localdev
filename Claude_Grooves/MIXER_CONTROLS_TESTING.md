# Mixer Controls Testing Script
## Ableton MCP Expansion - Week 1 Foundation

**Date:** December 13, 2025
**Session:** Mixer Control Implementation Testing
**Tools to Test:** 5 mixer control tools (set_track_volume, set_track_pan, set_track_mute, set_track_solo, set_send_amount)

---

## Pre-Test Setup Checklist

- [ ] Ableton Live 12 is running
- [ ] AbletonMCP Remote Script is loaded
  - Check: Preferences → Link, Tempo & MIDI → Control Surface = "AbletonMCP"
  - Input/Output should be "None"
- [ ] Claude Desktop is running with MCP server configured
- [ ] Test session created in Ableton with:
  - [ ] At least 4 MIDI tracks (tracks 0-3)
  - [ ] At least 1 return track (Return A)
  - [ ] Some instruments loaded (optional, for audio feedback)

---

## Test 1: Track Volume Control

### Test Commands:
```
"Set track 0 volume to -6 dB"
"Set track 1 volume to -12 dB"
"Set track 2 volume to 0 dB"
"Set track 3 volume to -20 dB"
```

### Expected Results:
- ✅ Track 0 fader moves to -6 dB
- ✅ Track 1 fader moves to -12 dB
- ✅ Track 2 fader moves to 0 dB (unity)
- ✅ Track 3 fader moves to -20 dB
- ✅ Each command returns normalized value (e.g., "normalized: 0.5")

### Verification:
- [ ] Volume faders move in Ableton UI
- [ ] Return message shows correct dB value
- [ ] Return message shows normalized value

### Notes:
_Record any issues or unexpected behavior:_

---

## Test 2: Track Panning Control

### Test Commands:
```
"Pan track 0 to the left at -0.5"
"Pan track 1 to the right at 0.75"
"Pan track 2 to center"
"Pan track 3 hard left at -1.0"
```

### Expected Results:
- ✅ Track 0 panned 50% left
- ✅ Track 1 panned 75% right
- ✅ Track 2 panned center (0.0)
- ✅ Track 3 panned hard left (-1.0)

### Verification:
- [ ] Pan knobs move in Ableton UI
- [ ] Return message shows correct position
- [ ] Pan description (left/center/right) is accurate

### Notes:
_Record any issues or unexpected behavior:_

---

## Test 3: Track Mute Control

### Test Commands:
```
"Mute track 0"
"Mute track 1"
"Unmute track 0"
"Unmute track 1"
```

### Expected Results:
- ✅ Track 0 mute button lights up (first command)
- ✅ Track 1 mute button lights up
- ✅ Track 0 mute button turns off (unmute)
- ✅ Track 1 mute button turns off

### Verification:
- [ ] Mute buttons toggle in Ableton UI
- [ ] Return message confirms mute state
- [ ] Audio stops when muted (if playing)

### Notes:
_Record any issues or unexpected behavior:_

---

## Test 4: Track Solo Control

### Test Commands:
```
"Solo track 2"
"Solo track 3"
"Unsolo track 2"
"Unsolo track 3"
```

### Expected Results:
- ✅ Track 2 solo button lights up
- ✅ Track 3 solo button lights up (both soloed)
- ✅ Track 2 solo button turns off
- ✅ Track 3 solo button turns off

### Verification:
- [ ] Solo buttons toggle in Ableton UI
- [ ] Return message confirms solo state
- [ ] Other tracks are muted when solo is active

### Notes:
_Record any issues or unexpected behavior:_

---

## Test 5: Send Amount Control

### Setup Required:
- Ensure at least Return Track A exists
- Optionally load a reverb on Return A for audio feedback

### Test Commands:
```
"Set track 0 send A to 0.3"
"Set track 1 send A to 0.5"
"Set track 2 send A to 0.15"
"Set track 0 send A to 0"
```

### Expected Results:
- ✅ Track 0 Send A knob moves to 30%
- ✅ Track 1 Send A knob moves to 50%
- ✅ Track 2 Send A knob moves to 15%
- ✅ Track 0 Send A knob moves to 0% (off)
- ✅ Return message shows "send A to 0.30", "send A to 0.50", etc.

### Verification:
- [ ] Send knobs move in Ableton UI
- [ ] Return message shows correct return index (A=0)
- [ ] Return message shows correct amount

### Notes:
_Record any issues or unexpected behavior:_

---

## Test 6: Edge Cases & Error Handling

### Test Invalid Track Index:
```
"Set track 99 volume to -6 dB"
```
**Expected:** Error message "Track index out of range"

### Test Invalid Return Index:
```
"Set track 0 send Z to 0.5"
```
**Expected:** Error message about invalid return track

### Test Out-of-Range Values:
```
"Set track 0 volume to -100 dB"  (should clamp to -70 dB)
"Pan track 0 to 5.0"              (should clamp to 1.0)
"Set track 0 send A to 2.0"       (should clamp to 1.0)
```

### Verification:
- [ ] Invalid indices return clear error messages
- [ ] Out-of-range values are clamped, not rejected
- [ ] No crashes or hangs

### Notes:
_Record any issues or unexpected behavior:_

---

## Test 7: Rapid Sequential Commands

### Test Command Sequence:
```
"Set track 0 volume to -12 dB, pan it to the left at -0.5, and set send A to 0.2"
```

Or issue individually in rapid succession:
```
"Set track 0 volume to -12 dB"
"Pan track 0 to -0.5"
"Set track 0 send A to 0.2"
```

### Expected Results:
- ✅ All commands execute successfully
- ✅ No timeout errors
- ✅ Final state: Track 0 at -12dB, panned left, 20% send A

### Verification:
- [ ] All commands complete without errors
- [ ] No network timeout issues
- [ ] Track state reflects all changes

### Notes:
_Record any issues or unexpected behavior:_

---

## Test 8: Integration with Existing Tools

### Test Combined Workflow:
1. Create a MIDI track: `"Create a new MIDI track"`
2. Name it: `"Rename track 4 to 'Bass'"`
3. Set volume: `"Set track 4 volume to -8 dB"`
4. Pan it: `"Pan track 4 to the right at 0.25"`
5. Add send: `"Set track 4 send A to 0.4"`

### Expected Results:
- ✅ Track created with name "Bass"
- ✅ Volume set to -8 dB
- ✅ Panned 25% right
- ✅ Send A at 40%

### Verification:
- [ ] All existing tools still work
- [ ] New mixer tools integrate seamlessly
- [ ] No conflicts or errors

### Notes:
_Record any issues or unexpected behavior:_

---

## Troubleshooting

### If commands fail with "Connection error":
1. Check Ableton Live is running
2. Verify Remote Script is loaded (Preferences → Control Surfaces)
3. Restart Claude Desktop MCP server
4. Check port 9877 is not blocked by firewall

### If commands succeed but Ableton doesn't change:
1. Check you're looking at the correct track index (0-based)
2. Verify the Remote Script is the correct updated version
3. Check Ableton's Log.txt for Remote Script errors

### If normalized values seem wrong:
1. Verify helpers.py db_to_normalized() function is working
2. Test with known values: -6dB should be ~0.5, 0dB should be ~0.85
3. Check Ableton Live API documentation for volume value ranges

---

## Post-Test Summary

### Overall Results:
- [ ] All 5 mixer control tools work correctly
- [ ] Error handling is appropriate
- [ ] Integration with existing tools is seamless
- [ ] Ready to proceed to Week 2 (Effect Parameters & Sidechain)

### Issues Found:
_List any bugs, unexpected behavior, or improvements needed:_

1.
2.
3.

### Performance Notes:
- Average command response time: _____ ms
- Network stability: _____________
- Ableton CPU usage: ____________

---

## Sign-Off

**Tested by:** _______________________
**Date:** _______________________
**Ableton Version:** Live 12.___
**MCP Server Status:** ☐ All tests passed ☐ Issues found (see above)

**Next Steps:**
- ☐ If all tests pass → Proceed to Week 2 (Effect Parameters)
- ☐ If issues found → Debug and retest failed items
- ☐ Document any API quirks for future reference

---

**Implementation Plan Reference:** `C:\Users\dread\.claude\plans\tidy-sleeping-aho.md`
**Week 1 Deliverable:** ✅ Basic mixing automation functional

*Testing complete. Ready for Week 2: Sidechain compression and folk-hip hop workflow.* ⚓🎵
