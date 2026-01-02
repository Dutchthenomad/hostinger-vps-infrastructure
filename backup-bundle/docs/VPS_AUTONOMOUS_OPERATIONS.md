# VPS Autonomous Operations Guide

**Created:** 2026-01-01
**Purpose:** Ensure VPS operates independently without local PC dependency

---

## Overview

The VPS RAG system is designed to operate **fully autonomously**. Once configured, it:
- Ingests live WebSocket data 24/7
- Stores vectors in Qdrant
- Stores time-series in TimescaleDB
- Serves RAG queries via MCP
- Requires **no local PC connection**

---

## 1. Architecture (Autonomous Mode)

```
┌────────────────────────────────────────────────────────────┐
│                  VPS (72.62.160.2)                         │
│                                                            │
│  ┌────────────────┐         ┌────────────────┐            │
│  │ Socket.IO      │────────▶│   RabbitMQ     │            │
│  │ Bridge         │         │   :5672        │            │
│  │ (auto-restart) │         │                │            │
│  └────────────────┘         └───────┬────────┘            │
│         ▲                           │                      │
│         │ WebSocket                 ▼                      │
│  ┌──────┴──────┐         ┌────────────────┐               │
│  │ rugs.fun    │         │     n8n        │               │
│  │ backend     │         │   Workflows    │               │
│  └─────────────┘         │   :5678        │               │
│                          └───────┬────────┘               │
│                                  │                         │
│                    ┌─────────────┴─────────────┐          │
│                    ▼                           ▼          │
│            ┌────────────┐              ┌────────────┐     │
│            │   Qdrant   │              │TimescaleDB │     │
│            │   :6333    │              │   :5433    │     │
│            │  (vectors) │              │  (events)  │     │
│            └────────────┘              └────────────┘     │
│                    │                           │          │
│                    └─────────────┬─────────────┘          │
│                                  │                         │
│                           ┌──────▼──────┐                  │
│                           │   MCP API   │◀───── Claude     │
│                           │ (n8n route) │       (any PC)   │
│                           └─────────────┘                  │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

---

## 2. Service Auto-Restart Configuration

All services are configured to restart automatically on failure or VPS reboot.

### Docker Compose Settings

```yaml
# /root/rag-stack/docker-compose.yml
services:
  n8n:
    restart: unless-stopped

  qdrant:
    restart: unless-stopped

  rabbitmq:
    restart: unless-stopped

  timescaledb:
    restart: unless-stopped

  socketio-bridge:
    restart: unless-stopped
```

### Verify Auto-Restart

```bash
# SSH to VPS
ssh hostinger-vps

# Simulate service crash
docker stop qdrant
sleep 5
docker ps | grep qdrant  # Should show running

# Simulate VPS reboot
sudo reboot

# After reboot, check all services
docker ps
# All 5+ containers should be running
```

---

## 3. Monitoring & Health Checks

### 3.1 Basic Health Check Script

Create `/root/scripts/health_check.sh`:

```bash
#!/bin/bash
# Health check for RAG stack

echo "=== RAG Stack Health Check ==="
echo "Time: $(date)"
echo ""

# Check Docker containers
echo "Docker Containers:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""

# Check Qdrant
echo "Qdrant Collections:"
curl -s "http://localhost:6333/collections" | jq -r '.result.collections[].name' 2>/dev/null || echo "ERROR: Qdrant not responding"
echo ""

# Check n8n
echo "n8n Status:"
curl -s "http://localhost:5678/healthz" && echo "OK" || echo "ERROR: n8n not responding"
echo ""

# Check RabbitMQ queue depth
echo "RabbitMQ Queues:"
curl -s -u n8n_rabbit:PASSWORD "http://localhost:15672/api/queues" | jq -r '.[].name' 2>/dev/null || echo "ERROR: RabbitMQ not responding"
echo ""

# Check TimescaleDB
echo "TimescaleDB Tables:"
docker exec timescaledb psql -U n8n_tsdb -d rugs_analytics -c "\dt" 2>/dev/null || echo "ERROR: TimescaleDB not responding"
echo ""

# Check disk space
echo "Disk Usage:"
df -h / | tail -1
echo ""

# Check memory
echo "Memory Usage:"
free -h | grep Mem
echo ""

echo "=== Health Check Complete ==="
```

### 3.2 Cron Job for Monitoring

```bash
# Add to crontab
crontab -e

# Add line (runs every hour, logs to file):
0 * * * * /root/scripts/health_check.sh >> /root/logs/health_check.log 2>&1
```

### 3.3 Alert on Failure (Optional)

```bash
# Simple failure detection script
#!/bin/bash
# /root/scripts/alert_on_failure.sh

if ! docker ps | grep -q qdrant; then
    echo "ALERT: Qdrant down at $(date)" >> /root/logs/alerts.log
    # Add email/webhook notification here
fi

if ! docker ps | grep -q n8n; then
    echo "ALERT: n8n down at $(date)" >> /root/logs/alerts.log
fi
```

---

## 4. Data Persistence

### 4.1 Volume Mounts

All data is persisted to host volumes:

```yaml
# docker-compose.yml volumes
volumes:
  qdrant_storage:
    driver: local

  n8n_data:
    driver: local

  postgres_data:
    driver: local

  timescaledb_data:
    driver: local

  rabbitmq_data:
    driver: local
```

### 4.2 Data Locations on VPS

```
/var/lib/docker/volumes/
├── rag-stack_qdrant_storage/     # Vector data
├── rag-stack_n8n_data/           # n8n workflows
├── rag-stack_postgres_data/      # n8n metadata
├── rag-stack_timescaledb_data/   # Time-series events
└── rag-stack_rabbitmq_data/      # Queue persistence
```

### 4.3 Backup Strategy

```bash
# Weekly backup script
#!/bin/bash
# /root/scripts/weekly_backup.sh

BACKUP_DIR="/root/backups/$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR

# Stop services for clean backup
cd /root/rag-stack
docker-compose stop

# Backup volumes
docker run --rm -v rag-stack_qdrant_storage:/data -v $BACKUP_DIR:/backup alpine tar czf /backup/qdrant.tar.gz /data
docker run --rm -v rag-stack_n8n_data:/data -v $BACKUP_DIR:/backup alpine tar czf /backup/n8n.tar.gz /data
docker run --rm -v rag-stack_timescaledb_data:/data -v $BACKUP_DIR:/backup alpine tar czf /backup/timescaledb.tar.gz /data

# Restart services
docker-compose start

echo "Backup complete: $BACKUP_DIR"
```

---

## 5. n8n Workflows (Autonomous)

### 5.1 Required Workflows

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| RAG Query | Webhook GET `/webhook/rag/query` | Serve RAG queries |
| WebSocket Ingestion | RabbitMQ trigger | Process incoming events |
| MCP Server | MCP trigger | Claude Code integration |

### 5.2 Workflow Auto-Activation

All workflows must be set to **Active** in n8n UI:
1. Open http://72.62.160.2:5678
2. Go to each workflow
3. Toggle "Active" switch ON

### 5.3 Error Handling

Each workflow should have:
- Error trigger node
- Logging to file or database
- Optional: webhook notification on failure

---

## 6. Socket.IO Bridge (Critical)

### 6.1 Bridge Requirements

The bridge must:
- Connect to `wss://backend.rugs.fun`
- Handle reconnection on disconnect
- Buffer events and batch to RabbitMQ
- Run 24/7 without intervention

### 6.2 Reconnection Logic

```javascript
// Built into bridge service
socket.on('disconnect', () => {
  console.log('Disconnected, reconnecting in 5s...');
  setTimeout(() => socket.connect(), 5000);
});

socket.on('connect_error', (err) => {
  console.log('Connection error:', err.message);
  setTimeout(() => socket.connect(), 10000);
});
```

### 6.3 Verify Bridge Running

```bash
# Check container
docker ps | grep socketio-bridge

# Check logs
docker logs -f socketio-bridge --tail 100

# Check RabbitMQ queue growing
curl -s -u n8n_rabbit:PASSWORD "http://localhost:15672/api/queues/n8n/websocket_events" | jq .messages
```

---

## 7. Accessing from Any PC

### 7.1 Claude Code MCP

From any PC with Claude Code installed:

```bash
# Add MCP server (one-time)
claude mcp add rugs-rag http://72.62.160.2:5678/mcp

# Use in Claude
claude
> Query the RAG about gameStateUpdate
```

### 7.2 Direct API Access

```bash
# From any machine with network access
curl "http://72.62.160.2:5678/webhook/rag/query?q=what%20is%20gameStateUpdate"
```

### 7.3 SSH Access

```bash
# Copy SSH key to new PC
scp ~/.ssh/hostinger_vps newpc:~/.ssh/

# On new PC, add to config
cat >> ~/.ssh/config << 'EOF'
Host hostinger-vps
    HostName 72.62.160.2
    User root
    IdentityFile ~/.ssh/hostinger_vps
EOF

# Connect
ssh hostinger-vps
```

---

## 8. Recovery Procedures

### 8.1 Service Won't Start

```bash
# Check logs
docker logs <container_name>

# Common fix: recreate container
cd /root/rag-stack
docker-compose down
docker-compose up -d
```

### 8.2 Qdrant Lost Vectors

```bash
# Re-run ingestion
python3 /root/scripts/ingest_knowledge.py

# Verify
curl "http://localhost:6333/collections/rugs_protocol" | jq .result.points_count
```

### 8.3 n8n Workflows Missing

```bash
# Restore from backup
docker cp /root/backups/n8n_workflows.json n8n:/home/node/.n8n/

# Or re-import manually via UI
```

### 8.4 Complete VPS Reset

```bash
# Nuclear option - rebuild everything
cd /root/rag-stack
docker-compose down -v  # WARNING: Destroys all data
docker-compose up -d

# Re-run all setup:
# 1. Create Qdrant collections
# 2. Run ingestion script
# 3. Restore n8n workflows
# 4. Rebuild Socket.IO bridge
```

---

## 9. Maintenance Schedule

| Task | Frequency | Command |
|------|-----------|---------|
| Health check | Hourly | Automated via cron |
| Log rotation | Daily | `logrotate` |
| Backup | Weekly | `/root/scripts/weekly_backup.sh` |
| Update containers | Monthly | `docker-compose pull && docker-compose up -d` |
| Disk cleanup | Monthly | `docker system prune -f` |

---

## 10. Key Contacts & Resources

### Hostinger VPS
- Control Panel: https://hpanel.hostinger.com
- Server: srv1216617.hstgr.cloud
- IP: 72.62.160.2

### Documentation
- This guide: `/root/docs/VPS_AUTONOMOUS_OPERATIONS.md`
- System architecture: `/root/docs/SYSTEM_ARCHITECTURE.md`
- Migration plan: `/root/docs/RAG_MIGRATION_PLAN.md`

### Logs
- Health checks: `/root/logs/health_check.log`
- Alerts: `/root/logs/alerts.log`
- Docker: `docker logs <container>`

---

*Guide created: 2026-01-01*
*VPS operates autonomously - no local PC required after initial setup*
