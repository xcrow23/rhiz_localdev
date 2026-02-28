# Archived Temp Workflow Files

**Archived**: 2026-01-11 (Session 41 - Batch 4 cleanup)
**Original Location**: Root directory (malformed path artifacts)
**Status**: Deprecated n8n workflow definitions

## Files Archived

### UsersdreadAppDataLocalTempdaily_health_workflow.json
- **Size**: 8.5 KB
- **Created**: 2026-01-03
- **Purpose**: Daily health check n8n workflow (Fathom Commander)
- **Malformed Path**: Indicates failed temp file creation during export

### UsersdreadAppDataLocalTempweekly_dca_workflow.json
- **Size**: 11 KB
- **Created**: 2026-01-03
- **Purpose**: Weekly dollar-cost averaging n8n workflow
- **Malformed Path**: Indicates failed temp file creation during export

## Why Malformed Paths?

These files were created with incorrect paths, likely due to:
1. Temp directory path not properly resolved (missing `\` separators)
2. Windows path handling issue in workflow export script
3. Should have been: `C:\Users\dread\AppData\Local\Temp\daily_health_workflow.json`
4. Instead got: `UsersdreadAppDataLocalTempdaily_health_workflow.json` (in root)

## Current Status

Both workflows are **deprecated** as of Session 40 (2026-01-10) per Captain's directive: "Abandon all hope ye who use n8n!"

These workflows are being migrated to **Cloudflare Workers** as documented in:
- `docs/architecture/N8N_TO_CLOUDFLARE_MIGRATION.md`

## Future Action

These files may provide useful reference during Cloudflare Workers migration to understand the original workflow logic. After migration is complete, they can be safely deleted.

---

**Archived**: 2026-01-11 (Session 41)
**Issue**: L2 (Low-Priority cleanup)
**Total Size**: 19.5 KB
