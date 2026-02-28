---
deployment: local-development
hardware: dell_inspiron_15_3535
os: windows_11_pro
status: operational
skills_system_active: true
memory_system_active: true
mcp_servers_active: 3
discovered_at: session_1_20251220
semantic_cluster: infrastructure_domain
vector_density: medium
threshold_recommendation: 0.30-0.40
last_updated: 2026-01-25
---

# Local Development Environment

**Machine**: Dell Inspiron 15 3535
**OS**: Windows 11 Pro
**Purpose**: Interactive development, skills routing, memory exploration
**Status**: Operational (skills active, local Qdrant, Ollama)

---

## Overview

The local development environment is Rhiz's **interactive workspace** where Captain and First Mate collaborate via Claude Code CLI. Unlike the VPS (24/7 automated operations), local development focuses on:

- **Skills system** (semantic routing, memory-augmented activation)
- **Memory exploration** (checkpoint search, semantic queries)
- **MCP tool development** (rhiz-mcp, memory-mcp)
- **Research & experimentation** (threshold tuning, pattern discovery)

**Intentional Asymmetry**: Skills system runs locally, not on VPS. Cloud handles deterministic workflows; local handles interactive pattern recognition.

---

## Hardware Specifications

### Dell Inspiron 15 3535

**CPU**:
- Model: AMD Ryzen 5 7530U
- Cores: 6 cores, 12 threads
- Base Clock: 2.0 GHz
- Boost Clock: 4.5 GHz (Zen 3 architecture)

**RAM**:
- Total: 16GB
- Available: ~15.4GB (after OS overhead)
- Type: DDR4

**Storage**:
- Type: SSD
- Size: Not specified (assume 512GB+)
- Usage: Project files, Docker volumes, checkpoints (~5GB)

**GPU**:
- Integrated: AMD Radeon Graphics (Zen 3 APU)
- No dedicated GPU (CPU-only inference)

**Constraints**:
- No CUDA (NVIDIA GPU required)
- Limited RAM (16GB shared between OS + Docker + apps)
- CPU-bound for local inference (Ollama)

---

## Software Stack

### Operating System

**OS**: Windows 11 Pro
**Version**: 23H2 (or newer)
**Build**: Not specified

**Why Windows**:
- Captain's primary machine
- WSL2 available for Linux containers
- Claude Code CLI supports Windows

### Docker Desktop

**Version**: Latest (20.10+)
**Backend**: WSL2 (Windows Subsystem for Linux)

**Resource Allocation**:
- RAM: Variable (Docker settings)
- CPU: Variable (Docker settings)
- Storage: ~50GB Docker volumes

**Status**: Qdrant container running (localhost:6333)

### Ollama (Local LLM Inference)

**Version**: Latest
**Port**: 11434
**Models**:
- qwen2.5-coder:7b (Mem0 LLM backend)
- nomic-embed-text:latest (Mem0 embeddings)
- (Other models as needed)

**Performance**:
- Inference speed: ~10-20 tokens/sec (CPU-only)
- Memory usage: ~4GB per model
- Startup time: <5 seconds

**Use Cases**:
- Mem0 memory extraction
- Skill context processing
- (Not used for Claude Code - that's Anthropic API)

### Python Environment

**Version**: 3.10+
**Virtual Environments**: venv or conda
**Key Packages**:
- pyyaml (checkpoints)
- qdrant-client (vector search)
- mem0ai (skill memory)
- anthropic (Claude API - for rhiz-mcp)

---

## Local Services

### 1. Qdrant (Vector Database)

**Deployment**: Docker container
**Port**: 6333 (localhost only)
**Storage**: Docker volume (persistent)

**Collections**:
- `rhiz_memories`: 161 vectors (38 checkpoints)
- `rhiz_skills`: 6 vectors (skill fingerprints)
- `rhiz_skill_memory`: 8 vectors (Mem0 memories)

**Configuration**:
```yaml
# docker-compose.local.yaml (conceptual)
services:
  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
    volumes:
      - qdrant_storage:/qdrant/storage
    environment:
      - QDRANT_ALLOW_RECOVERY_MODE=true
```

**Performance**:
- Search latency: 10-50ms
- Startup time: <2 seconds
- Memory usage: ~500MB

### 2. Ollama (LLM Inference)

**Deployment**: Native Windows app
**Port**: 11434
**Models Directory**: `%USERPROFILE%\.ollama\models`

**Configuration**:
```bash
# Environment variables
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODELS=%USERPROFILE%\.ollama\models
```

**Performance**:
- Model load time: 2-5 seconds
- Inference: 10-20 tokens/sec (qwen2.5-coder:7b)
- Memory per model: ~4GB

**Status**: Running, used by Mem0 for skill memory extraction

### 3. Claude Code CLI

**Deployment**: Native Windows app (installed via npm)
**Purpose**: Interactive AI-human collaboration
**Configuration**: `~/.claude/config.json`

**MCP Servers Configured**:
- rhiz-mcp (11 tools - dyad state, checkpoints, memory)
- memory-mcp (6 tools - semantic search)
- (fathom, github, hostinger, fetch, etc. as needed)

**Status**: Active (current session)

---

## MCP Servers (Local)

### 1. rhiz-mcp (11 tools)

**Location**: `tools/rhiz-mcp/`
**Protocol**: stdio
**Purpose**: Dyad state, checkpoint management, memory context

**Tools**:
- `get_dyad_state`, `set_captain_state`, `update_shared_focus`
- `checkpoint_search`, `load_checkpoint`, `write_checkpoint`
- `memory_context`, `hybrid_search_checkpoints`
- `signal_completion`, `propose_focus_shift`

**Status**: Operational

### 2. memory-mcp (6 tools)

**Location**: `tools/memory-mcp/`
**Protocol**: stdio
**Purpose**: Semantic search across checkpoints

**Tools**:
- `memory_search`, `memory_search_by_date`, `memory_get_recent_sessions`
- `memory_store`, `memory_stats`, `memory_health_check`

**Backend**: Qdrant localhost:6333, collection `rhiz_memories`

**Status**: Operational

### 3. fathom (8 tools - Phase 1)

**Location**: `domains/trading/fathom/`
**Protocol**: stdio
**Purpose**: Kraken exchange interaction

**Tools**:
- `fathom_health_check`, `fathom_get_balance`, `fathom_get_ticker`
- `fathom_get_orderbook`, `fathom_get_ohlc`, etc.

**Status**: Configured, operational for Phase 1 tools

**Note**: Fathom also deployed to VPS but local instance used for interactive sessions

---

## Skills System (Local Only)

**Why Local Only**: Skills are for interactive pattern recognition during development. Cloud handles deterministic workflows, not skill routing.

**Components**:
- **Semantic Router**: Qdrant (`rhiz_skills` collection, threshold 0.25)
- **Skill Definitions**: `core/skills/registry/`
- **Mem0 Backend**: Qdrant (`rhiz_skill_memory` collection)
- **Ollama LLM**: qwen2.5-coder:7b for memory extraction

**Performance**:
- Routing: <10ms (semantic search)
- Memory retrieval: 200-500ms (Mem0 + Ollama)
- Total activation: <600ms

**Skills Defined** (6 total):
1. trading/kraken_analysis
2. memory/session_management
3. memory/checkpoint_retrieval
4. research/documentation
5. infrastructure/deployment
6. infrastructure/troubleshooting

**Accuracy**: 93.3% (28/30 test cases)

---

## Memory System (Local)

**Checkpoint Storage**: Filesystem (`core/memory/checkpoints/`)
- Format: YAML
- Count: 38 files
- Size: 380KB total
- Schema compliance: 100%

**Vector Storage**: Qdrant localhost:6333
- `rhiz_memories`: 161 vectors (checkpoints)
- `rhiz_skill_memory`: 8 vectors (skill contexts)

**Session Hooks**:
- `session_start.py`: Load dyad state + skill context
- (session_end manually triggered via checkpoint write)

**Status**: Fully operational

---

## Development Workflow

### Session Start

1. **Open Claude Code CLI** (Windows Terminal)
2. **Session hook runs** (automatic):
   - Updates dyad state (session count++)
   - Loads latest checkpoint
   - Searches relevant memories
   - Loads skill context (if domains active)
3. **First Mate ready** with full context

**Typical Output**:
```
[session_start] Session 74
[session_start] Dyad state updated
[session_start] Skill Context: 1 skill memories loaded - trading/kraken_analysis
```

### Interactive Development

**Use Cases**:
- **Memory exploration**: `memory_search "first trade execution"`
- **Checkpoint analysis**: `load_checkpoint session_20251226_wave2_first_trade.yaml`
- **Skill testing**: Route queries to skills, validate accuracy
- **Research**: Threshold tuning, pattern discovery
- **Documentation**: Write architecture docs, extract checkpoint knowledge

### Session End

1. **Write checkpoint** (manually or via tool):
   ```
   write_checkpoint({
     session_arc: "...",
     decisions_made: [...],
     ...
   })
   ```
2. **Checkpoint saved** to `core/memory/checkpoints/`
3. **Checkpoint embedded** to Qdrant `rhiz_memories`
4. **Session complete**

---

## Resource Usage (Typical)

### Idle State
- **RAM**: ~8GB (OS: 4GB, Docker: 2GB, Apps: 2GB)
- **CPU**: <5%
- **Disk**: 60GB (OS + Apps + Docker)

### Active Development (Claude Code + Qdrant + Ollama)
- **RAM**: ~12GB (OS: 4GB, Docker: 3GB, Ollama: 4GB, Apps: 1GB)
- **CPU**: 20-40% (during Ollama inference, otherwise <10%)
- **Disk**: Same (minimal writes)

**Headroom**: 4GB RAM available (comfortable)

**Bottleneck**: Ollama inference (CPU-bound, no GPU acceleration)

---

## Local vs VPS Comparison

| Aspect | Local (Dell Inspiron) | VPS (Hostinger) |
|--------|----------------------|-----------------|
| **Purpose** | Interactive development | 24/7 automation |
| **Skills System** | ✅ Active (93.3% accuracy) | ❌ Not deployed (by design) |
| **Memory** | Qdrant localhost:6333 | Qdrant + PostgreSQL |
| **Trading** | Manual (via Claude Code) | Automated (n8n workflows) |
| **Deployment** | Docker Desktop | Docker Compose |
| **Uptime** | When Captain's PC on | 24/7 |
| **Resource** | 16GB RAM, 6 CPU | 16GB RAM, 4 vCPU |
| **Cost** | $0 (owned hardware) | ~$20-30/month |

**Synergy**: Local handles interactive work, VPS handles automation. Complementary roles.

---

## Known Issues

### Issue 1: Ollama Performance (CPU-Only)

**Problem**: Ollama inference slow (10-20 tokens/sec) vs GPU-accelerated (100+ tokens/sec)

**Impact**: Mem0 memory extraction takes 2-3 seconds

**Workaround**: Acceptable for session start (only happens once per session)

**Future**: Upgrade to GPU-enabled machine or use cloud inference

### Issue 2: Docker Desktop Resource Limits

**Problem**: Docker Desktop RAM/CPU limits not explicitly configured

**Risk**: Docker may consume excessive resources during intensive operations

**Resolution**: Set explicit limits in Docker Desktop settings

### Issue 3: No Automated Backups (Local)

**Problem**: Checkpoints on local disk only (no cloud backup)

**Risk**: PC failure = checkpoint loss

**Resolution**: Implement cloud sync (Qdrant localhost → VPS Qdrant)

**Status**: Manual sync via memory-sync tool (not automated)

---

## Future Enhancements

### Enhancement 1: Local GPU (Future Hardware)

**Target**: AMD RX 6600 or NVIDIA RTX 3060
**Benefit**: 10x faster Ollama inference (100+ tokens/sec)
**Cost**: ~$200-300 GPU
**Priority**: Low (current performance acceptable)

### Enhancement 2: RAM Upgrade (32GB)

**Target**: 32GB DDR4
**Benefit**: More headroom for Docker, Ollama, multiple models
**Cost**: ~$60-80
**Priority**: Low (16GB sufficient for now)

### Enhancement 3: Automated Checkpoint Sync

**Target**: Cron job (or Windows Task Scheduler)
**Benefit**: Local checkpoints backed up to VPS Qdrant
**Implementation**: `memory-sync` tool scheduled daily
**Priority**: Medium

---

## Cross-References

**Source Code**:
- `infrastructure/docker/` - Local Docker configurations
- `infrastructure/local/` - Dell Inspiron-specific configs

**Component Documentation**:
- `docs/knowledge_base/components/skills_system.md` - Skills (local only)
- `docs/knowledge_base/components/memory_system.md` - Dual deployment (local + VPS)

**Related Documentation**:
- `docs/knowledge_base/deployments/vps_topology.md` - Cloud deployment
- `docs/research/semantic_routing_accuracy_optimization.md` - Threshold tuning (local work)

---

**End of Deployment Documentation**

*Last Updated: 2026-01-25 (Session 74)*
*Status: Operational (skills active, Qdrant running, Ollama functional)*
*Purpose: Interactive development & pattern recognition*
