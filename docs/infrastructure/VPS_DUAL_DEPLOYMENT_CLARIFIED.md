# VPS Infrastructure Clarification
**Generated**: 2026-01-10 (Session 40 - Comprehensive Audit)
**Status**: DUAL VPS DEPLOYMENT (Not a migration)

## TL;DR

We have **TWO separate VPS instances** serving different purposes, NOT one replacing the other.

## VPS Topology

### VPS 1: Hostinger KVM4 (72.62.81.128)
**Purpose**: Legacy trading infrastructure + n8n orchestration
**Deployed**: January 3, 2026
**Status**: ✅ Operational

**Services**:
- **Fathom Commander** (port 8766) - 27 MCP tools for trading workflow orchestration
- **Traefik** (ports 80/443) - SSL termination via Let's Encrypt
- **n8n** (local instance) - 9 workflows (SIL health monitor, strategy selection, etc.)
- **Qdrant** - rhiz_memories collection (174 vectors as of Jan 3)
- **Docker containers**: Multiple trading-related services

**Networking**:
- Public IP: 72.62.81.128
- DNS: fathom.dreamthewilderness.com → 72.62.81.128 (Cloudflare proxied)
- HTTPS: https://fathom.dreamthewilderness.com/ (SSL via Traefik + Let's Encrypt)
- Direct access: http://72.62.81.128:8766/

**Key Files**:
- `docs/architecture/deployment_summary_20260103.md` (deployment documentation)
- `docs/architecture/fathom_commander_cloud_deployment_plan.md` (architecture)
- `core/memory/checkpoints/session_20260103_infrastructure_operational.yaml` (operational checkpoint)

---

### VPS 2: Hetzner (95.217.51.24)
**Purpose**: Cloudflare Workers support infrastructure (FastAPI Gateway + Cloud Qdrant)
**Deployed**: Late December 2025 (exact date TBD - check mooncheck session)
**Status**: ✅ Operational (SSH access issues noted)

**Services**:
- **FastAPI Gateway** - Backend for Cloudflare Workers (mooncheck integration)
- **Embedding Service** - Vector embedding generation for memory system
- **Qdrant Cloud** (port 6333) - moonchecks collection (separate from rhiz_memories)
- **n8n** (version 2.2.5) - Migration target for trading workflows (in progress)

**Networking**:
- Public IP: 95.217.51.24
- SSH: Port 22 (connection refused as of Jan 10 - firewall or auth issue)
- Qdrant: 95.217.51.24:6333 (operational, cloud sync working)

**Purpose Alignment**:
- Supports mooncheck Cloudflare Workers deployment (✅ Complete)
- Target for n8n → Cloudflare Workers migration for trading workflows (⏳ Pending)
- Hosts cloud Qdrant instance separate from local rhiz_memories

**Key Files**:
- `infrastructure/vps/fastapi_gateway.py` (FastAPI Gateway source)
- `infrastructure/vps/embedding_service.py` (Embedding service source)
- `infrastructure/vps/DEPLOYMENT_GUIDE.md` (deployment instructions)
- `docs/infrastructure/VPS_INTEGRATION_REVIEW_20260110.md` (integration review)

---

## Architecture Rationale

### Why Two VPS Instances?

**Separation of Concerns**:
1. **VPS 1 (Hostinger)**: Legacy infrastructure for established trading systems
   - Fathom Commander proven operational
   - n8n workflows running production strategies
   - Traefik SSL for domain-based routing

2. **VPS 2 (Hetzner)**: New serverless-first architecture
   - Supports Cloudflare Workers (no local state, all via API)
   - FastAPI Gateway bridges Workers ↔ VPS services
   - Cloud Qdrant for moonchecks (separate use case from session memories)

**NOT a Migration**: The plan was never to shut down Hostinger and move everything to Hetzner. Instead:
- Mooncheck deployed to Cloudflare Workers + Hetzner VPS (✅ Complete)
- Trading workflows will eventually migrate from Hostinger n8n → Cloudflare Workers + Hetzner VPS (⏳ In Progress)
- Both VPS instances may run in parallel during transition

---

## Service Distribution Matrix

| Service | VPS 1 (Hostinger) | VPS 2 (Hetzner) | Status |
|---------|-------------------|-----------------|--------|
| **Fathom Commander** | ✅ Port 8766 | ❌ | Operational |
| **Traefik** | ✅ Ports 80/443 | ❌ | Operational |
| **n8n** | ✅ 9 workflows | ⏳ Version 2.2.5 | Migration in progress |
| **Qdrant** | ✅ rhiz_memories | ✅ moonchecks | Dual deployment |
| **FastAPI Gateway** | ❌ | ✅ | Operational (mooncheck) |
| **Embedding Service** | ❌ | ✅ | Operational |

---

## Resolution Actions

### Immediate (Completed)
- ✅ Documented dual VPS topology (this file)
- ✅ Clarified VPS 1 = Hostinger, VPS 2 = Hetzner
- ✅ Updated CLAUDE.md with VPS info
- ✅ Updated ALIGNMENT_ISSUES_TRACKER.md (C12 resolved)

### Short-Term (Next Sessions)
- 🔲 Debug SSH access to VPS 2 (95.217.51.24)
- 🔲 Update `cloud_deployment_topology.md` to reflect dual VPS architecture
- 🔲 Verify n8n migration status (Hostinger → Hetzner for trading workflows)
- 🔲 Confirm Qdrant dual deployment is intentional (rhiz_memories vs moonchecks)

### Medium-Term
- 🔲 Decide on long-term VPS strategy:
  - Option A: Consolidate to single VPS (Hetzner) once migration complete
  - Option B: Keep dual deployment (trading on Hostinger, serverless on Hetzner)
  - Option C: Migrate everything to Cloudflare Workers + minimal VPS footprint

---

## Historical Context

**Pre-Jan 3**: No VPS deployment, all local (laptop Docker)
**Jan 3**: Hostinger VPS deployed for Fathom Commander (trading infrastructure)
**Late Dec**: Hetzner VPS added for Cloudflare Workers support (mooncheck)
**Jan 10**: Clarification session to resolve "VPS identity crisis"

---

## Questions Resolved

**Q**: Are 72.62.81.128 and 95.217.51.24 the same VPS?
**A**: No. They are two separate VPS instances serving different purposes.

**Q**: Did we migrate from Hostinger to Hetzner?
**A**: No. Hetzner was added for new Cloudflare Workers infrastructure, not to replace Hostinger.

**Q**: Why does documentation reference both IPs?
**A**: Because both are operational. Older docs (Jan 3) reference Hostinger. Newer docs (mooncheck deployment) reference Hetzner.

**Q**: Which VPS should be used for new services?
**A**: Depends on architecture:
- Trading/n8n workflows → Hostinger (legacy) or migrate to Cloudflare Workers + Hetzner (new)
- Cloudflare Workers support → Hetzner
- Local-only services → Neither (run on laptop Docker)

---

## Deployment Decision Tree

```
New service deployment?
│
├─ Pure Cloudflare Worker (no state, no VPS)?
│  └─ Deploy to Cloudflare Workers only
│
├─ Cloudflare Worker needing VPS backend?
│  └─ Deploy Worker to Cloudflare + FastAPI Gateway to Hetzner VPS
│
├─ Trading-related (Fathom, SIL)?
│  ├─ Legacy approach → Hostinger VPS + n8n
│  └─ New approach → Cloudflare Workers + Hetzner VPS
│
└─ Local development/testing?
   └─ Laptop Docker (no VPS)
```

---

## Related Documentation

- `docs/architecture/cloud_deployment_topology.md` (needs update)
- `docs/architecture/deployment_summary_20260103.md` (Hostinger VPS)
- `docs/infrastructure/VPS_INTEGRATION_REVIEW_20260110.md` (identified the confusion)
- `infrastructure/vps/DEPLOYMENT_GUIDE.md` (Hetzner VPS)
- `infrastructure/cloudflare/checkpoint-api/DEPLOYMENT_STEPS.md` (Cloudflare Workers)

---

**Status**: VPS Identity Crisis RESOLVED
**Next Action**: Update cloud_deployment_topology.md to reflect dual VPS architecture
