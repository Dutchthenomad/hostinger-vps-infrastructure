# n8n Connection Reference for RAG Stack

> **n8n UI Access**: http://72.62.160.2:5678
>
> This document contains all connection details for configuring n8n credentials and nodes.

---

## Quick Reference Table

| Service | Internal Host | Port | Protocol | Credential Type |
|---------|---------------|------|----------|-----------------|
| Qdrant | `qdrant` | 6333 | HTTP | None (no auth) |
| RabbitMQ | `rabbitmq` | 5672 | AMQP | RabbitMQ |
| TimescaleDB | `timescaledb` | 5432 | PostgreSQL | Postgres |

---

## 1. Qdrant (Vector Database)

**Use in n8n**: Qdrant Vector Store node

### Connection Details

| Setting | Value |
|---------|-------|
| **URL** | `http://qdrant:6333` |
| **API Key** | *(leave empty - no auth configured)* |
| **Collection** | `rugs_events_v2` *(create in workflow)* |

### Testing Connection

```bash
# From VPS terminal
curl http://localhost:6333/collections
```

### n8n Credential Setup

1. Go to **Credentials** → **Add Credential**
2. Search for **Qdrant API**
3. Enter:
   - **URL**: `http://qdrant:6333`
   - **API Key**: *(leave blank)*

---

## 2. RabbitMQ (Message Queue)

**Use in n8n**: RabbitMQ Trigger node, RabbitMQ node

### Connection Details

| Setting | Value |
|---------|-------|
| **Hostname** | `rabbitmq` |
| **Port** | `5672` |
| **Virtual Host** | `n8n` |
| **Username** | `n8n_rabbit` |
| **Password** | `14Pay4QL9Q57dy5ssQff7cBz7WRUysyR` |

### Queues Available

| Queue | Purpose |
|-------|---------|
| `websocket_events` | Main event queue (max 100k messages, DLX enabled) |
| `dead_events` | Dead-letter queue for failed messages |

### Management UI

- **URL**: http://72.62.160.2:15672
- **Username**: `n8n_rabbit`
- **Password**: `14Pay4QL9Q57dy5ssQff7cBz7WRUysyR`

### n8n Credential Setup

1. Go to **Credentials** → **Add Credential**
2. Search for **RabbitMQ**
3. Enter:
   - **Hostname**: `rabbitmq`
   - **Port**: `5672`
   - **User**: `n8n_rabbit`
   - **Password**: `14Pay4QL9Q57dy5ssQff7cBz7WRUysyR`
   - **Virtual Host**: `n8n`

---

## 3. TimescaleDB (Analytics Database)

**Use in n8n**: Postgres node

### Connection Details

| Setting | Value |
|---------|-------|
| **Host** | `timescaledb` |
| **Port** | `5432` |
| **Database** | `rugs_analytics` |
| **Username** | `n8n_tsdb` |
| **Password** | `gosQ6UPmlTr28dWAaChUPr0Omkfjdu7Q` |
| **SSL** | Disable |

### Connection String

```
postgresql://n8n_tsdb:gosQ6UPmlTr28dWAaChUPr0Omkfjdu7Q@timescaledb:5432/rugs_analytics
```

### Tables Available

| Table | Description |
|-------|-------------|
| `websocket_events` | Hypertable for time-series events |

### Schema

```sql
websocket_events (
    time        TIMESTAMPTZ NOT NULL,
    event_type  TEXT NOT NULL,
    game_id     TEXT,
    payload     JSONB,
    source      TEXT DEFAULT 'n8n'
)
```

### n8n Credential Setup

1. Go to **Credentials** → **Add Credential**
2. Search for **Postgres**
3. Enter:
   - **Host**: `timescaledb`
   - **Database**: `rugs_analytics`
   - **User**: `n8n_tsdb`
   - **Password**: `gosQ6UPmlTr28dWAaChUPr0Omkfjdu7Q`
   - **Port**: `5432`
   - **SSL**: Off

---

## External Access URLs

For accessing services from your local machine (outside the VPS):

| Service | External URL |
|---------|--------------|
| **n8n** | http://72.62.160.2:5678 |
| **RabbitMQ Management** | http://72.62.160.2:15672 |
| **Qdrant Dashboard** | http://72.62.160.2:6333/dashboard |
| **TimescaleDB** | `postgresql://n8n_tsdb:PASSWORD@72.62.160.2:5433/rugs_analytics` |

> **Note**: TimescaleDB external port is `5433` (not 5432) to avoid conflict with n8n-postgres.

---

## First Workflow: Test All Connections

Create this workflow in n8n to verify all services are connected:

### Workflow: "RAG Stack Health Check"

```
[Manual Trigger]
      ↓
[HTTP Request: GET http://qdrant:6333/collections]
      ↓
[Postgres: SELECT NOW() FROM websocket_events LIMIT 1]
      ↓
[Set: Combine results]
```

This confirms:
1. Qdrant is responding
2. TimescaleDB connection works
3. RabbitMQ (test via separate RabbitMQ Trigger workflow)

---

## Troubleshooting

### "Connection refused" errors

All services use **internal Docker hostnames** (`qdrant`, `rabbitmq`, `timescaledb`), not `localhost`. Ensure you're using the internal names in n8n credentials.

### RabbitMQ authentication failed

Verify the virtual host is set to `n8n` (not `/` or empty).

### Qdrant collection not found

Create the collection first via workflow or API:
```bash
curl -X PUT http://qdrant:6333/collections/rugs_events_v2 \
  -H "Content-Type: application/json" \
  -d '{"vectors": {"size": 384, "distance": "Cosine"}}'
```

---

## Next Steps

1. Open n8n UI at http://72.62.160.2:5678
2. Create credentials for each service (see setup sections above)
3. Create your first workflow using RabbitMQ Trigger → Process → Qdrant/TimescaleDB
