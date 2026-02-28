# TRACE Confidence Scoring

**Source**: SynLang Manifesto (Kapusta, June 2025)  
**Integration Date**: 2026-01-01  
**Purpose**: Enable transparent AI uncertainty communication and trust calibration

---

## Theory

SynLang's **TRACE/TRACE_FE protocol** enables AI to communicate confidence levels alongside reasoning:

- **TRACE**: High-level reasoning patterns
- **TRACE_FE**: Factor explanations with confidence scores

Example from research:
```
TRACE: thermal_anomaly, known_failure_mode
TRACE_FE:
- thermal_anomaly: temperature exceeded safe thresholds (confidence=0.91)
- known_failure_mode: matches historic incidents (confidence=0.89)
```

##Implementation in Rhiz

Confidence scores are now embedded in checkpoint `working_memory`:

```yaml
working_memory:
  mental_model: "Dyad state is now operational"
  confidence: 0.92  # Overall confidence in mental model
  
  hypotheses:
    - text: "Hooks may need Claude Code config"
      confidence: 0.65  # Uncertainty about this hypothesis
    - text: "YAML parser is production-ready"
      confidence: 0.95  # High confidence
      
  active_context: "Wave 2 daemon layer"
```

---

## Confidence Scale

- **0.9-1.0**: High confidence - verified through testing or documentation
- **0.7-0.9**: Medium-high - logical deduction with some uncertainty
- **0.5-0.7**: Medium - educated guess, needs validation
- **0.3-0.5**: Low-medium - speculative, significant uncertainty
- **0.0-0.3**: Low - highly uncertain, flag for verification

---

## Use Cases

1. **Trust Calibration**: Captain learns which confidence levels are reliable
2. **Priority Signaling**: Low-confidence hypotheses need testing first
3. **Decision Quality**: Track correlation between confidence and outcomes
4. **Transparency**: Makes AI uncertainty visible instead of hidden

---

## Future Integration (Wave 5)

- **Confidence tracking over time**: Did high-confidence claims prove correct?
- **Calibration metrics**: Is AI over/under-confident?
- **Automated testing**: Low-confidence items trigger validation workflows
- **Learning feedback**: Adjust confidence estimation based on outcomes

---

## Related Research

- **SYMBIOSIS_SYNTHESIS_20251223.md** (lines 56-69): Original TRACE/TRACE_FE explanation
- **The_Emergent_Dyad-Research.md** (lines 75-88): Trust under uncertainty discussion
