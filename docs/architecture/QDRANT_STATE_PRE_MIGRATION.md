# Qdrant Collections State - Pre-Migration Snapshot
**Date**: 2026-01-11
**Session**: 42 - Unified Trading Platform Migration

## Current Deployment

**Hetzner VPS**: 95.217.51.24
**Qdrant Version**: v1.7.4 (Docker)
**Port**: 6333

## Existing Collections

### 1. rhiz_memories
**Purpose**: Session checkpoint persistence for human-AI collaboration
**Vector Size**: 384 (all-MiniLM-L6-v2)
**Point Count**: 174 vectors
**Created**: 2025-12-22
**Last Updated**: 2026-01-10

**Schema**:
```yaml
vector_size: 384
distance: Cosine
payload_fields:
  - session_id: string
  - created: datetime
  - session_topic: string
  - content: text (checkpoint YAML content)
```

**Sample Point**:
```json
{
  "id": "session_20260110_comprehensive_audit_wave",
  "vector": [0.123, -0.456, ...],  // 384 dimensions
  "payload": {
    "session_id": "session_20260110_comprehensive_audit_wave",
    "created": "2026-01-10T22:45:00",
    "session_topic": "Comprehensive audit, C6 resolution, Batch 4 cleanup",
    "checkpoint_path": "core/memory/checkpoints/session_20260110_comprehensive_audit_wave.yaml"
  }
}
```

### 2. moonchecks
**Purpose**: Cloudflare Workers permaculture data storage
**Vector Size**: 384 (all-MiniLM-L6-v2)
**Point Count**: ~50 (estimated, cloud data)
**Created**: 2026-01-08
**Last Updated**: 2026-01-11

**Schema**:
```yaml
vector_size: 384
distance: Cosine
payload_fields:
  - timestamp: datetime
  - source: string (e.g., "cloudflare_worker")
  - permaculture_data: object
  - summary: text
```

**Sample Point**:
```json
{
  "id": "mooncheck_20260108_001",
  "vector": [0.234, 0.567, ...],  // 384 dimensions
  "payload": {
    "timestamp": "2026-01-08T12:00:00",
    "source": "cloudflare_worker",
    "permaculture_data": {
      "season": "winter",
      "location": "midwest",
      "analysis": "Dormancy period, focus on planning"
    }
  }
}
```

## Post-Migration: New Collection

### 3. trading_signals (TO BE CREATED)
**Purpose**: Unified trading intelligence substrate - cross-system learning
**Vector Size**: 384 (all-MiniLM-L6-v2)
**Point Count**: 0 (initial)
**Distance**: Cosine

**Schema**:
```yaml
vector_size: 384
distance: Cosine
payload_indexes:
  - signal_type: keyword (decision, regime, pattern)
  - pair: keyword (BTC/USD, ETH/USD, etc.)
  - source: keyword (fathom, fc, sil)
payload_fields:
  - timestamp: datetime
  - signal_type: enum [decision, regime, pattern]
  - source: enum [fathom, fc, sil]
  - pair: string
  - data: object (flexible JSON blob per source)
```

**Sample Points**:

**Fathom Decision**:
```json
{
  "id": "dec_abc123",
  "vector": [embedding of decision context],
  "payload": {
    "timestamp": "2026-01-11T15:30:00",
    "signal_type": "decision",
    "source": "fathom",
    "pair": "BTC/USD",
    "data": {
      "side": "buy",
      "amount": 0.001,
      "price": 45230,
      "reasoning": "Breakout after 48h consolidation, volume spike",
      "hypothesis": "Breakouts after consolidation succeed 60% of time",
      "spread": 0.02,
      "outcome": "pending",
      "pnl": null
    }
  }
}
```

**SIL Regime**:
```json
{
  "id": "reg_xyz789",
  "vector": [embedding of regime classification],
  "payload": {
    "timestamp": "2026-01-11T15:25:00",
    "signal_type": "regime",
    "source": "sil",
    "pair": "BTC/USD",
    "data": {
      "regime": "bull_strong_trend",
      "confidence": 0.87,
      "volatility_regime": "low",
      "recommended_strategy": "momentum_scalping",
      "indicators": {
        "rsi": 62,
        "macd": "bullish",
        "volume_profile": "increasing"
      }
    }
  }
}
```

## Backup Strategy

**Pre-Migration Snapshot**:
```bash
# Snapshot rhiz_memories collection
curl http://95.217.51.24:6333/collections/rhiz_memories/snapshots -X POST

# Snapshot moonchecks collection
curl http://95.217.51.24:6333/collections/moonchecks/snapshots -X POST

# List snapshots
curl http://95.217.51.24:6333/collections/rhiz_memories/snapshots
curl http://95.217.51.24:6333/collections/moonchecks/snapshots
```

**Post-Migration Verification**:
```bash
# Verify all 3 collections exist
curl http://95.217.51.24:6333/collections | jq '.result.collections[].name'
# Expected: ["rhiz_memories", "moonchecks", "trading_signals"]

# Verify point counts
curl http://95.217.51.24:6333/collections/rhiz_memories | jq '.result.points_count'  # Should be 174
curl http://95.217.51.24:6333/collections/moonchecks | jq '.result.points_count'     # Should be ~50
curl http://95.217.51.24:6333/collections/trading_signals | jq '.result.points_count'  # Should be 0 initially
```

## Migration Checklist

- [ ] Snapshot rhiz_memories (Captain to execute)
- [ ] Snapshot moonchecks (Captain to execute)
- [ ] Verify snapshots created
- [ ] Proceed with VPS consolidation
- [ ] Create trading_signals collection (Phase 1, Step 1.4)
- [ ] Verify all 3 collections post-migration
