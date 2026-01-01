# RAG Stack Setup Guide

This document describes the RAG (Retrieval-Augmented Generation) infrastructure deployed on the Hostinger VPS.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         VPS (72.62.160.2)                       │
│                                                                  │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐    │
│  │     n8n      │────▶│   RabbitMQ   │────▶│  TimescaleDB │    │
│  │   :5678      │     │   :5672      │     │    :5433     │    │
│  │  (Webhooks)  │     │  (Buffering) │     │ (Time-series)│    │
│  └──────────────┘     └──────────────┘     └──────────────┘    │
│         │                                                       │
│         │              ┌──────────────┐                        │
│         └─────────────▶│    Qdrant    │                        │
│                        │   :6333      │                        │
│                        │  (Vectors)   │                        │
│                        └──────────────┘                        │
│                                                                  │
│  ┌──────────────┐                                               │
│  │   Postgres   │◀── n8n backend storage                       │
│  │   :5432      │                                               │
│  └──────────────┘                                               │
└─────────────────────────────────────────────────────────────────┘
```

## Components

### 1. n8n (Workflow Automation)
- **Purpose**: HTTP webhooks, workflow orchestration, service integration
- **Port**: 5678
- **Backend**: PostgreSQL
- **Email**: Resend SMTP integration

### 2. Qdrant (Vector Database)
- **Purpose**: Store embeddings for RAG retrieval
- **Ports**: 6333 (HTTP), 6334 (gRPC)
- **Features**: Scalar quantization for memory efficiency

### 3. RabbitMQ (Message Queue)
- **Purpose**: Buffer real-time WebSocket events before processing
- **Ports**: 5672 (AMQP), 15672 (Management UI)
- **Queues**:
  - `websocket_events` - Main event queue
  - `dead_events` - Dead letter queue

### 4. TimescaleDB (Time-Series Database)
- **Purpose**: Store time-series analytics data
- **Port**: 5433
- **Features**: Hypertables with automatic compression

## Deployment

### Prerequisites

1. SSH access to VPS: `ssh hostinger-vps`
2. Docker and Docker Compose installed
3. n8n stack already running

### Deploy RAG Stack

```bash
# SSH to VPS
ssh hostinger-vps

# Navigate to rag-stack directory
cd /root/rag-stack

# Start services
docker-compose up -d

# Verify all containers are running
docker ps
```

### Initialize Services

#### RabbitMQ Queues

```bash
# Create virtual host
docker exec rabbitmq rabbitmqctl add_vhost n8n

# Create user and permissions
docker exec rabbitmq rabbitmqctl add_user n8n_rabbit '<password>'
docker exec rabbitmq rabbitmqctl set_permissions -p n8n n8n_rabbit ".*" ".*" ".*"

# Create queues via management API
docker exec rabbitmq rabbitmqadmin -u n8n_rabbit -p '<password>' -V n8n \
  declare queue name=websocket_events durable=true \
  arguments='{"x-dead-letter-exchange":"","x-dead-letter-routing-key":"dead_events"}'

docker exec rabbitmq rabbitmqadmin -u n8n_rabbit -p '<password>' -V n8n \
  declare queue name=dead_events durable=true
```

#### TimescaleDB Schema

```bash
docker exec -i timescaledb psql -U n8n_tsdb -d rugs_analytics << 'EOF'
-- Create hypertable for WebSocket events
CREATE TABLE IF NOT EXISTS websocket_events (
    id BIGSERIAL,
    event_type TEXT NOT NULL,
    game_id TEXT,
    player_id TEXT,
    payload JSONB NOT NULL,
    raw_message TEXT,
    received_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    processed_at TIMESTAMPTZ,
    source TEXT DEFAULT 'websocket',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Convert to hypertable
SELECT create_hypertable('websocket_events', 'created_at',
    chunk_time_interval => INTERVAL '1 day',
    if_not_exists => TRUE);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_ws_events_type ON websocket_events(event_type);
CREATE INDEX IF NOT EXISTS idx_ws_events_game ON websocket_events(game_id);
CREATE INDEX IF NOT EXISTS idx_ws_events_time ON websocket_events(created_at DESC);

-- Enable compression
ALTER TABLE websocket_events SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'event_type'
);

-- Add compression policy (compress chunks older than 7 days)
SELECT add_compression_policy('websocket_events', INTERVAL '7 days', if_not_exists => true);
EOF
```

## n8n Configuration

### Required Credentials

Create these in n8n UI (Settings → Credentials):

1. **TimescaleDB Analytics** (PostgreSQL)
   - Host: `timescaledb`
   - Port: `5432`
   - Database: `rugs_analytics`
   - User: `n8n_tsdb`

2. **RabbitMQ HTTP** (HTTP Basic Auth)
   - User: `n8n_rabbit`

### Workflow Import

Import workflows from `/home/nomad/Desktop/VPS/n8n-workflows/`:

1. `02-simple-rag-health.json` - Basic health check

## Verification

### Health Check Endpoint

```bash
curl http://72.62.160.2:5678/webhook/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2026-01-01T06:18:57.884Z",
  "qdrant": {
    "status": "ok",
    "collections": []
  },
  "message": "RAG Stack is operational"
}
```

### Service Status

```bash
# Check all containers
ssh hostinger-vps 'docker ps --format "table {{.Names}}\t{{.Status}}"'

# Check Qdrant
curl http://72.62.160.2:6333/collections

# Check RabbitMQ
curl -u n8n_rabbit:<password> http://72.62.160.2:15672/api/queues/n8n

# Check TimescaleDB
ssh hostinger-vps 'docker exec timescaledb psql -U n8n_tsdb -d rugs_analytics -c "SELECT count(*) FROM websocket_events;"'
```

## Troubleshooting

### Container not starting

```bash
# Check logs
docker logs <container_name>

# Check network connectivity
docker exec n8n ping qdrant
docker exec n8n ping rabbitmq
docker exec n8n ping timescaledb
```

### Webhook not responding

1. Ensure workflow is **published** (not just saved)
2. Check n8n logs: `docker logs n8n`
3. Verify network: `curl -v http://localhost:5678/webhook/health` from VPS

### Database connection issues

```bash
# Test TimescaleDB connection
docker exec timescaledb psql -U n8n_tsdb -d rugs_analytics -c "SELECT 1;"

# Test RabbitMQ
docker exec rabbitmq rabbitmqctl list_queues -p n8n
```

## Next Steps

1. **WebSocket Ingestion Pipeline** - Consume Socket.IO events → RabbitMQ → n8n → Storage
2. **Embedding Pipeline** - Process events → Generate embeddings → Store in Qdrant
3. **Query API** - RAG retrieval endpoints for agentic access
