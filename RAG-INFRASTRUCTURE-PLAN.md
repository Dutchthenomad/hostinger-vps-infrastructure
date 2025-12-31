# RAG Infrastructure Stack Deployment Plan

> **Status**: READY TO EXECUTE
> **Created**: 2025-12-29
> **Target**: srv1216617 VPS

---

## Current Environment Snapshot

| Resource | Value | Status |
|----------|-------|--------|
| **Disk Space** | 36 GB free | OK (need ~20GB) |
| **RAM** | 3.8 GB total, ~2.6 GB available | TIGHT (need ~4GB) |
| **Docker Network** | `n8n_default` (bridge) | Target network |
| **Existing Containers** | n8n, n8n-postgres | DO NOT MODIFY |

### Existing Docker Setup
```
CONTAINER        IMAGE              NETWORK
n8n              n8nio/n8n:latest   n8n_default
n8n-postgres     postgres:16        n8n_default
```

---

## Services to Deploy

### 1. Qdrant (Vector Database)

| Setting | Value |
|---------|-------|
| Image | `qdrant/qdrant:latest` |
| Ports | 6333 (HTTP), 6334 (gRPC) |
| Storage | On-disk (not in-memory) |
| Quantization | Scalar (memory efficient) |
| Volume | `qdrant_data` |

**Purpose**: Store embeddings for RAG retrieval of WebSocket events and documentation.

### 2. RabbitMQ (Message Queue)

| Setting | Value |
|---------|-------|
| Image | `rabbitmq:3-management` |
| Ports | 5672 (AMQP), 15672 (Management UI) |
| vHost | `n8n` |
| Queue Limits | x-max-length=100000, dead-letter routing |
| Volume | `rabbitmq_data` |

**Purpose**: Buffer real-time WebSocket events for processing by n8n workflows.

### 3. TimescaleDB (Time-Series Analytics)

| Setting | Value |
|---------|-------|
| Image | `timescale/timescaledb:latest-pg15` |
| Port | 5433 (avoid conflict with n8n-postgres on 5432) |
| Database | `rugs_analytics` |
| Volume | `timescaledb_data` |

**Purpose**: Store time-series analytics data from WebSocket events for historical analysis.

---

## Deployment Files

### File 1: `/root/rag-stack/docker-compose.yml`

```yaml
version: '3.8'

services:
  qdrant:
    image: qdrant/qdrant:latest
    container_name: qdrant
    restart: unless-stopped
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - qdrant_data:/qdrant/storage
    environment:
      - QDRANT__STORAGE__ON_DISK_PAYLOAD=true
      - QDRANT__STORAGE__QUANTIZATION__SCALAR__ALWAYS_RAM=false
    networks:
      - n8n_default
    healthcheck:
      test: ["CMD", "wget", "-q", "--spider", "http://localhost:6333/"]
      interval: 30s
      timeout: 10s
      retries: 3

  rabbitmq:
    image: rabbitmq:3-management
    container_name: rabbitmq
    restart: unless-stopped
    ports:
      - "5672:5672"
      - "15672:15672"
    volumes:
      - rabbitmq_data:/var/lib/rabbitmq
    environment:
      - RABBITMQ_DEFAULT_USER=${RABBITMQ_USER}
      - RABBITMQ_DEFAULT_PASS=${RABBITMQ_PASS}
      - RABBITMQ_DEFAULT_VHOST=n8n
    networks:
      - n8n_default
    healthcheck:
      test: ["CMD", "rabbitmq-diagnostics", "-q", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  timescaledb:
    image: timescale/timescaledb:latest-pg15
    container_name: timescaledb
    restart: unless-stopped
    ports:
      - "5433:5432"
    volumes:
      - timescaledb_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_USER=${TIMESCALE_USER}
      - POSTGRES_PASSWORD=${TIMESCALE_PASS}
      - POSTGRES_DB=rugs_analytics
    networks:
      - n8n_default
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${TIMESCALE_USER} -d rugs_analytics"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  qdrant_data:
  rabbitmq_data:
  timescaledb_data:

networks:
  n8n_default:
    external: true
```

### File 2: `/root/rag-stack/.env`

```bash
# Generated credentials - CHANGE THESE OR REGENERATE
RABBITMQ_USER=n8n_rabbit
RABBITMQ_PASS=<GENERATE_32_CHAR_RANDOM>

TIMESCALE_USER=n8n_tsdb
TIMESCALE_PASS=<GENERATE_32_CHAR_RANDOM>
```

**Generate secure passwords with:**
```bash
openssl rand -base64 32 | tr -dc 'a-zA-Z0-9' | head -c 32
```

---

## Execution Steps

### Phase 1: Pre-flight Checks

```bash
# 1. Verify disk space (need 20GB+)
df -h /

# 2. Verify RAM (need ~4GB available)
free -h

# 3. Confirm n8n is running and healthy
docker ps | grep n8n

# 4. Verify network exists
docker network ls | grep n8n_default
```

### Phase 2: Create Directory Structure

```bash
# Create rag-stack directory
mkdir -p /root/rag-stack
cd /root/rag-stack

# Create docker-compose.yml (copy from above)
# Create .env with generated passwords
```

### Phase 3: Generate Credentials

```bash
cd /root/rag-stack

# Generate .env file with secure passwords
cat > .env << 'EOF'
RABBITMQ_USER=n8n_rabbit
RABBITMQ_PASS=$(openssl rand -base64 32 | tr -dc 'a-zA-Z0-9' | head -c 32)

TIMESCALE_USER=n8n_tsdb
TIMESCALE_PASS=$(openssl rand -base64 32 | tr -dc 'a-zA-Z0-9' | head -c 32)
EOF

# Actually generate the passwords
RABBIT_PASS=$(openssl rand -base64 32 | tr -dc 'a-zA-Z0-9' | head -c 32)
TSDB_PASS=$(openssl rand -base64 32 | tr -dc 'a-zA-Z0-9' | head -c 32)

cat > .env << EOF
RABBITMQ_USER=n8n_rabbit
RABBITMQ_PASS=${RABBIT_PASS}

TIMESCALE_USER=n8n_tsdb
TIMESCALE_PASS=${TSDB_PASS}
EOF

echo "Credentials saved to .env"
```

### Phase 4: Deploy Services (One at a Time)

```bash
cd /root/rag-stack

# Start Qdrant first
docker compose up -d qdrant
sleep 10
docker ps | grep qdrant
curl -s http://localhost:6333/collections | head

# Start RabbitMQ
docker compose up -d rabbitmq
sleep 15
docker ps | grep rabbitmq
curl -s -u n8n_rabbit:${RABBIT_PASS} http://localhost:15672/api/overview | head

# Start TimescaleDB
docker compose up -d timescaledb
sleep 10
docker ps | grep timescaledb
docker exec timescaledb pg_isready -U n8n_tsdb -d rugs_analytics
```

### Phase 5: Verify All Services

```bash
# Check all containers are running
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "(qdrant|rabbitmq|timescaledb)"

# Verify network connectivity from n8n's perspective
docker exec n8n wget -q -O- http://qdrant:6333/collections
docker exec n8n nc -zv rabbitmq 5672
docker exec n8n nc -zv timescaledb 5432
```

---

## n8n Connection Details

After deployment, use these connection strings in n8n:

### Qdrant (Vector Store)

| Field | Value |
|-------|-------|
| **Host** | `qdrant` (internal) or `localhost` (external) |
| **Port** | 6333 |
| **URL** | `http://qdrant:6333` |
| **API Key** | None (not configured) |

### RabbitMQ (Message Queue)

| Field | Value |
|-------|-------|
| **Host** | `rabbitmq` |
| **Port** | 5672 |
| **vHost** | `n8n` |
| **Username** | `n8n_rabbit` |
| **Password** | (from .env file) |
| **Management UI** | `http://YOUR_IP:15672` |

### TimescaleDB (PostgreSQL)

| Field | Value |
|-------|-------|
| **Host** | `timescaledb` |
| **Port** | 5432 (internal), 5433 (external) |
| **Database** | `rugs_analytics` |
| **Username** | `n8n_tsdb` |
| **Password** | (from .env file) |
| **Connection String** | `postgresql://n8n_tsdb:PASSWORD@timescaledb:5432/rugs_analytics` |

---

## Post-Deployment: RabbitMQ Queue Setup

After RabbitMQ is running, create the queue with limits:

```bash
# Access RabbitMQ container
docker exec -it rabbitmq bash

# Create queue with dead-letter routing
rabbitmqadmin -u n8n_rabbit -p PASSWORD declare queue \
  name=websocket_events \
  durable=true \
  arguments='{"x-max-length": 100000, "x-dead-letter-exchange": "dlx", "x-dead-letter-routing-key": "dead_events"}'

# Create dead-letter exchange and queue
rabbitmqadmin -u n8n_rabbit -p PASSWORD declare exchange name=dlx type=direct durable=true
rabbitmqadmin -u n8n_rabbit -p PASSWORD declare queue name=dead_events durable=true
rabbitmqadmin -u n8n_rabbit -p PASSWORD declare binding source=dlx destination=dead_events routing_key=dead_events

exit
```

---

## Post-Deployment: TimescaleDB Schema

After TimescaleDB is running, create the initial schema:

```bash
docker exec -it timescaledb psql -U n8n_tsdb -d rugs_analytics << 'EOF'

-- Create hypertable for WebSocket events
CREATE TABLE IF NOT EXISTS websocket_events (
    time        TIMESTAMPTZ NOT NULL,
    event_type  TEXT NOT NULL,
    game_id     TEXT,
    payload     JSONB,
    source      TEXT DEFAULT 'n8n'
);

SELECT create_hypertable('websocket_events', 'time', if_not_exists => TRUE);

-- Create index for common queries
CREATE INDEX IF NOT EXISTS idx_events_type ON websocket_events (event_type, time DESC);
CREATE INDEX IF NOT EXISTS idx_events_game ON websocket_events (game_id, time DESC);

-- Enable compression for older data (after 7 days)
ALTER TABLE websocket_events SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'event_type'
);

SELECT add_compression_policy('websocket_events', INTERVAL '7 days', if_not_exists => TRUE);

\dt
\di

EOF
```

---

## Firewall Rules (Optional)

If you need external access to management UIs:

```bash
# RabbitMQ Management UI
ufw allow 15672/tcp comment 'RabbitMQ Management'

# Qdrant API (only if needed externally)
# ufw allow 6333/tcp comment 'Qdrant API'

# TimescaleDB (only if needed externally)
# ufw allow 5433/tcp comment 'TimescaleDB'
```

---

## Rollback Plan

If something goes wrong:

```bash
cd /root/rag-stack

# Stop all new services
docker compose down

# Remove volumes if needed (DATA LOSS!)
docker compose down -v

# Verify n8n is still running
docker ps | grep n8n
```

---

## Resource Estimates

| Service | RAM | Disk | CPU |
|---------|-----|------|-----|
| Qdrant | ~500MB-1GB | ~5GB | Low |
| RabbitMQ | ~256MB-512MB | ~1GB | Low |
| TimescaleDB | ~512MB-1GB | ~10GB+ | Medium |
| **Total** | **~1.5-2.5GB** | **~16GB** | Low-Medium |

**Note**: Current server has ~2.6GB available RAM. This is tight but should work with on-disk storage configurations.

---

## Quick Start Command

Once files are in place, deploy everything with:

```bash
cd /root/rag-stack
docker compose up -d
docker compose ps
```

---

## Checklist

- [ ] Pre-flight checks passed (disk, RAM, network)
- [ ] `/root/rag-stack/` directory created
- [ ] `docker-compose.yml` created
- [ ] `.env` file created with secure passwords
- [ ] Qdrant deployed and healthy
- [ ] RabbitMQ deployed and healthy
- [ ] TimescaleDB deployed and healthy
- [ ] Network connectivity verified from n8n
- [ ] Queue with dead-letter routing created
- [ ] TimescaleDB schema created
- [ ] Connection details documented
- [ ] Credentials saved securely
