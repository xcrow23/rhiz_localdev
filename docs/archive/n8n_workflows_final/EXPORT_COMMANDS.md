# n8n Workflow Export Commands
**Date**: 2026-01-11
**Session**: 42 - Unified Trading Platform Migration

## Export All Workflows

Execute these commands on **Hostinger VPS** before migration:

```bash
# SSH to Hostinger
ssh root@72.62.81.128

# Navigate to n8n directory
cd /opt/n8n

# Export all workflows to JSON
docker exec -it n8n n8n export:workflow --all --output=/data/workflows_final_export_20260111.json

# Copy export to local machine
exit

# From local machine
scp root@72.62.81.128:/opt/n8n/workflows_final_export_20260111.json ~/rhiz_localdev/docs/archive/n8n_workflows_final/
```

## Workflows to be Archived

### Fathom Commander Workflows (10)
1. `daily_health_monitor_workflow.json` - Daily 8AM CT health checks
2. `weekly_dca_buyer_workflow.json` - Sunday 6PM CT, $15 BTC purchases (LIVE)
3. `heartbeat_workflow.json` - 60s polling
4. `risk_monitor_workflow.json` - Real-time risk assessment
5. `spread_scanner_workflow.json` - Spread opportunity detection
6. `portfolio_rebalance_workflow.json` - Weekly portfolio rebalancing
7. `market_data_collector_workflow.json` - OHLCV data collection
8. `order_status_checker_workflow.json` - Order fill verification
9. `emergency_stop_workflow.json` - Circuit breaker trigger
10. `performance_reporter_workflow.json` - Weekly performance summary

### Strategic Intelligence Layer Workflows (3)
1. `mooncheck_workflow_complete.json` - Permaculture analysis (migrated to Cloudflare)
2. `regime_classifier_workflow.json` - Market regime detection
3. `pattern_learner_workflow.json` - Pattern recognition updates

## Post-Export Verification

```bash
# Verify export file size (should be >100 KB)
ls -lh ~/rhiz_localdev/docs/archive/n8n_workflows_final/workflows_final_export_20260111.json

# Count workflows in export
cat ~/rhiz_localdev/docs/archive/n8n_workflows_final/workflows_final_export_20260111.json | jq '. | length'
# Should show: 13

# Preview workflow names
cat ~/rhiz_localdev/docs/archive/n8n_workflows_final/workflows_final_export_20260111.json | jq '.[].name'
```

## Archive Logs

```bash
# Archive n8n logs from Hostinger
ssh root@72.62.81.128 "cd /opt/n8n && tar -czf n8n_logs_archive_20260111.tar.gz logs/"

# Copy logs to local
scp root@72.62.81.128:/opt/n8n/n8n_logs_archive_20260111.tar.gz ~/rhiz_localdev/docs/archive/n8n_workflows_final/
```

## Status

- [ ] Workflows exported (Captain to execute)
- [ ] Export file verified (13 workflows)
- [ ] Logs archived
- [ ] Files copied to local archive directory
