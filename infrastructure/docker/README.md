# Docker Infrastructure

This directory contains Docker-specific configuration files and utilities for the Rhiz project.

## Directory Structure

```
infrastructure/docker/
├── README.md                    # This file
├── docker-compose.prod.yml      # Production overrides (future)
├── health-checks.sh             # Container health monitoring
└── backup-volumes.sh            # Docker volume backup script
```

## Usage

### Main Orchestration

The primary `docker-compose.yml` is located at the project root:
```bash
cd /c/Users/dread/Documents/Rhiz/origin
docker-compose up -d
```

### Production Overrides

For production deployments (future cloud VPS):
```bash
docker-compose -f docker-compose.yml -f infrastructure/docker/docker-compose.prod.yml up -d
```

## Container Architecture

```
┌─────────────────────────────────────────────┐
│  HOST: Dell Inspiron 15 3535                │
│  OS: Windows 11 Pro                         │
│  Docker: 28.5.2                             │
└──────────────┬──────────────────────────────┘
               │
       ┌───────┴────────┐
       │  rhiz_network  │  (172.28.0.0/16)
       └───────┬────────┘
               │
       ┌───────┴──────────────────────────┐
       │                                   │
   ┌───▼─────┐  ┌──────────┐  ┌────────┐
   │Hummingbot│  │ LocalAI  │  │ Redis  │
   │  :2GB    │  │  :8GB    │  │ :512MB │
   │  2 CPUs  │  │  4 CPUs  │  │ 1 CPU  │
   └──────────┘  └──────────┘  └────────┘
```

## Resource Allocation

Total available: 16GB RAM, 12 CPU threads

| Service | RAM Limit | CPU Limit | Purpose |
|---------|-----------|-----------|---------|
| Hummingbot | 2GB | 2 cores | Trading bot runtime |
| LocalAI | 8GB | 4 cores | Local model inference |
| Redis | 512MB | 1 core | Session state & queuing |
| Reserved | 5.5GB | 5 cores | Windows OS + Claude Desktop |

## Health Monitoring

Check all containers:
```bash
docker ps
docker stats rhiz_hummingbot rhiz_localai rhiz_redis
```

Run health checks:
```bash
./infrastructure/docker/health-checks.sh
```

## Backup Strategy

Docker volumes contain critical data:
- `domains/trading/hummingbot/conf/` - Trading bot configuration
- `domains/trading/hummingbot/logs/` - Trade execution logs
- `redis_data` - Session state

Backup script:
```bash
./infrastructure/docker/backup-volumes.sh
```

## Network Security

All services bind to `127.0.0.1` only:
- LocalAI: http://localhost:8080
- Redis: localhost:6379
- Hummingbot: Interactive via `docker attach`

No external network exposure by default.

## Troubleshooting

### Container won't start
```bash
docker-compose logs [service_name]
docker-compose restart [service_name]
```

### Out of memory
```bash
docker stats
# Adjust mem_limit in docker-compose.yml if needed
```

### Port already in use
```bash
netstat -ano | findstr :<port>
# Kill the process or change port in docker-compose.yml
```

### Hummingbot lost connection
```bash
docker attach rhiz_hummingbot
# Check status, exit bot
# Update API keys in .env
docker-compose restart hummingbot
```

## Future Enhancements

- [ ] Grafana dashboard for metrics
- [ ] Automated backup to Hostinger
- [ ] Watchtower for auto-updates (currently disabled)
- [ ] n8n local instance (currently cloud-only)
