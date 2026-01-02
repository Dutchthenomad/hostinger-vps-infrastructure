# Unified RAG Migration Plan

**Created:** 2026-01-01
**Updated:** 2026-01-01 (Added Phase 0 for PC migration)
**Status:** Ready for Execution
**Target:** VPS srv1216617 (Hostinger)

---

## Executive Summary

This plan consolidates all rugs.fun knowledge from the local machine into the VPS n8n stack for vectorized RAG retrieval. The VPS infrastructure is **80% complete** - Qdrant, RabbitMQ, and TimescaleDB are running. This plan covers the remaining 20%: knowledge ingestion, workflow creation, and MCP integration.

**CRITICAL UPDATE:** Local PC is failing. Phase 0 added to ensure complete documentation export for restoration on new PC. VPS must operate fully autonomously after migration.

---

## Related Documentation

| Document | Purpose |
|----------|---------|
| [SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md) | Complete system overview |
| [NEW_PC_RESTORATION_GUIDE.md](NEW_PC_RESTORATION_GUIDE.md) | Step-by-step restoration |
| [VPS_AUTONOMOUS_OPERATIONS.md](VPS_AUTONOMOUS_OPERATIONS.md) | VPS self-operation guide |

---

## Current State

### VPS Infrastructure (COMPLETE)

| Service | Status | Port | Purpose |
|---------|--------|------|---------|
| n8n | Running | 5678 | Workflow automation |
| Qdrant | Running | 6333 | Vector database |
| RabbitMQ | Running | 5672 | Message queue |
| TimescaleDB | Running | 5433 | Time-series analytics |
| n8n-postgres | Running | 5432 | n8n metadata |

### Local Knowledge Sources

| Source | Size | Files | Priority | Action |
|--------|------|-------|----------|--------|
| `rugipedia/` | 788 KB | 29 | P0 | Ingest to Qdrant |
| `rl-design/` | 52 KB | 5 | P1 | Ingest to Qdrant |
| `rugs_recordings/` | 401 MB | 13 | P2 | Process → TimescaleDB |
| `RAG SUPERPACK/` | 1.7 GB | 37 repos | P3 | Extract docs only |
| `rag-pipeline/` | ~5 MB | N/A | N/A | Code only, don't ingest |

---

## Phase 0: Documentation Export (CRITICAL)

**Purpose:** Create complete documentation for PC restoration before hardware failure.

### 0.1 Verify Documentation Created

```bash
# Check all docs exist
ls -la ~/Desktop/VPS/docs/

# Should see:
# - SYSTEM_ARCHITECTURE.md      (complete system overview)
# - NEW_PC_RESTORATION_GUIDE.md (step-by-step restore)
# - VPS_AUTONOMOUS_OPERATIONS.md (VPS self-operation)
# - RAG_MIGRATION_PLAN.md       (this file)
# - N8N_CONNECTION_REFERENCE.md (connection details)
# - RAG_STACK_SETUP.md          (initial setup)
```

### 0.2 Copy Critical Files to VPS

```bash
# Upload documentation to VPS for safekeeping
rsync -avz ~/Desktop/VPS/docs/ hostinger-vps:/root/docs/

# Upload SSH key backup (encrypted)
# NOTE: Store SSH key securely - needed for new PC access
```

### 0.3 Export Claude Code Configuration

```bash
# Document current MCP servers
claude mcp list > ~/Desktop/VPS/docs/mcp_servers_backup.txt

# Document installed plugins
ls -la ~/.claude/plugins/ > ~/Desktop/VPS/docs/plugins_backup.txt

# Copy any custom CLAUDE.md
cp ~/CLAUDE.md ~/Desktop/VPS/docs/CLAUDE_HOME_BACKUP.md
```

### 0.4 Create Portable Backup Bundle

```bash
# Create backup bundle for new PC
mkdir -p ~/Desktop/VPS/backup-bundle

# Copy SSH keys (CRITICAL)
cp ~/.ssh/hostinger_vps* ~/Desktop/VPS/backup-bundle/

# Copy all VPS docs
cp -r ~/Desktop/VPS/docs ~/Desktop/VPS/backup-bundle/

# Copy SSH config
cp ~/.ssh/config ~/Desktop/VPS/backup-bundle/ssh_config

# Create tarball for easy transfer
cd ~/Desktop/VPS
tar -czvf backup-bundle.tar.gz backup-bundle/

echo "Backup bundle created: ~/Desktop/VPS/backup-bundle.tar.gz"
echo "Copy this to USB/cloud for new PC setup"
```

### 0.5 Verify VPS Accessible Without Local PC

```bash
# Test VPS services respond to public API
curl -s "http://72.62.160.2:5678/healthz"

# Test Qdrant accessible (should work from any IP)
curl -s "http://72.62.160.2:6333/collections"
```

---

## Phase 1: Knowledge Export (Local)

### 1.1 Package Rugipedia for Upload

```bash
# Create export directory
mkdir -p ~/Desktop/VPS/knowledge-export

# Copy rugipedia (canonical knowledge)
cp -r ~/Desktop/claude-flow/knowledge/rugipedia ~/Desktop/VPS/knowledge-export/

# Copy rl-design
cp -r ~/Desktop/claude-flow/knowledge/rl-design ~/Desktop/VPS/knowledge-export/

# Create manifest
find ~/Desktop/VPS/knowledge-export -name "*.md" -o -name "*.json" | wc -l > ~/Desktop/VPS/knowledge-export/MANIFEST.txt
du -sh ~/Desktop/VPS/knowledge-export/* >> ~/Desktop/VPS/knowledge-export/MANIFEST.txt
```

### 1.2 Extract RAG SUPERPACK Documentation

The full 1.7GB is too large for VPS (32GB free). Extract only markdown/docs:

```bash
cd ~/Desktop/claude-flow/knowledge/RAG\ SUPERPACK

# Create docs-only export
mkdir -p ~/Desktop/VPS/knowledge-export/external-docs

# Copy index files
cp RAG_KNOWLEDGE_SOURCES.md ~/Desktop/VPS/knowledge-export/external-docs/
cp RISK_MANAGEMENT_SOURCES.md ~/Desktop/VPS/knowledge-export/external-docs/
cp SOLANA_FORENSICS_SOURCES.md ~/Desktop/VPS/knowledge-export/external-docs/

# Extract README files from each repo (high-value summaries)
find . -name "README.md" -exec cp --parents {} ~/Desktop/VPS/knowledge-export/external-docs/ \;

# Extract docs folders where they exist
find . -type d -name "docs" -exec cp -r --parents {} ~/Desktop/VPS/knowledge-export/external-docs/ \; 2>/dev/null
```

### 1.3 Convert Game Recordings to Events

```bash
# Create JSONL export for TimescaleDB ingestion
mkdir -p ~/Desktop/VPS/knowledge-export/game-events

# Copy recordings
cp -r ~/rugs_recordings/*.jsonl ~/Desktop/VPS/knowledge-export/game-events/
```

---

## Phase 2: Upload to VPS

### 2.1 Sync via rsync

```bash
# From local machine
rsync -avz --progress ~/Desktop/VPS/knowledge-export/ hostinger-vps:/root/knowledge/

# Verify upload
ssh hostinger-vps "du -sh /root/knowledge/*"
```

### 2.2 Expected VPS Directory Structure

```
/root/
├── rag-stack/           # Docker infrastructure
│   ├── docker-compose.yml
│   └── .env
├── knowledge/           # Uploaded content (NEW)
│   ├── rugipedia/
│   │   ├── canon/
│   │   │   ├── WEBSOCKET_EVENTS_SPEC.md
│   │   │   ├── CONNECTION_DIAGRAM.md
│   │   │   └── PROVABLY_FAIR_VERIFICATION.md
│   │   ├── blockchain/
│   │   ├── game-modes/
│   │   └── generated/
│   ├── rl-design/
│   │   ├── observation-space-design.md
│   │   ├── action-space-design.md
│   │   └── implementation-plan.md
│   ├── external-docs/
│   │   ├── RAG_KNOWLEDGE_SOURCES.md
│   │   ├── RISK_MANAGEMENT_SOURCES.md
│   │   └── [extracted READMEs]
│   └── game-events/
│       └── *.jsonl
└── scripts/
    └── ingest_knowledge.py  # NEW - bulk ingestion script
```

---

## Phase 3: Qdrant Ingestion

### 3.1 Create Collections

```bash
# SSH to VPS
ssh hostinger-vps

# Create collections via Qdrant API
curl -X PUT "http://localhost:6333/collections/rugs_protocol" \
  -H "Content-Type: application/json" \
  -d '{
    "vectors": {
      "size": 384,
      "distance": "Cosine"
    },
    "optimizers_config": {
      "default_segment_number": 2
    },
    "quantization_config": {
      "scalar": {
        "type": "int8",
        "always_ram": false
      }
    }
  }'

# Create RL design collection
curl -X PUT "http://localhost:6333/collections/rl_design" \
  -H "Content-Type: application/json" \
  -d '{
    "vectors": {
      "size": 384,
      "distance": "Cosine"
    }
  }'

# Create external docs collection
curl -X PUT "http://localhost:6333/collections/external_docs" \
  -H "Content-Type: application/json" \
  -d '{
    "vectors": {
      "size": 384,
      "distance": "Cosine"
    }
  }'
```

### 3.2 Bulk Ingestion Script

Create `/root/scripts/ingest_knowledge.py`:

```python
#!/usr/bin/env python3
"""
Bulk ingest markdown knowledge into Qdrant.
Requires: pip install sentence-transformers qdrant-client
"""

import os
import hashlib
from pathlib import Path
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct

# Configuration
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
KNOWLEDGE_DIR = "/root/knowledge"
COLLECTIONS = {
    "rugipedia": "rugs_protocol",
    "rl-design": "rl_design",
    "external-docs": "external_docs"
}

# Load embedding model (384 dimensions)
model = SentenceTransformer('all-MiniLM-L6-v2')
client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

def chunk_text(text: str, max_chars: int = 1000) -> list[str]:
    """Split text into chunks at paragraph boundaries."""
    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = ""

    for para in paragraphs:
        if len(current_chunk) + len(para) < max_chars:
            current_chunk += para + "\n\n"
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = para + "\n\n"

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks

def ingest_folder(folder: str, collection: str):
    """Ingest all markdown files from folder into collection."""
    folder_path = Path(KNOWLEDGE_DIR) / folder
    if not folder_path.exists():
        print(f"Skipping {folder} - not found")
        return

    points = []
    point_id = 0

    for md_file in folder_path.rglob("*.md"):
        print(f"Processing: {md_file.name}")

        try:
            content = md_file.read_text(encoding='utf-8')
        except Exception as e:
            print(f"  Error reading {md_file}: {e}")
            continue

        chunks = chunk_text(content)

        for i, chunk in enumerate(chunks):
            if len(chunk.strip()) < 50:
                continue

            # Generate embedding
            embedding = model.encode(chunk).tolist()

            # Create unique ID from content hash
            chunk_id = hashlib.md5(f"{md_file}:{i}".encode()).hexdigest()

            points.append(PointStruct(
                id=chunk_id,
                vector=embedding,
                payload={
                    "text": chunk,
                    "source": str(md_file.relative_to(KNOWLEDGE_DIR)),
                    "chunk_index": i,
                    "total_chunks": len(chunks)
                }
            ))
            point_id += 1

    # Batch upsert
    if points:
        client.upsert(collection_name=collection, points=points)
        print(f"Inserted {len(points)} chunks into {collection}")

def main():
    for folder, collection in COLLECTIONS.items():
        print(f"\n=== Ingesting {folder} → {collection} ===")
        ingest_folder(folder, collection)

    print("\n=== Collection Stats ===")
    for collection in COLLECTIONS.values():
        try:
            info = client.get_collection(collection)
            print(f"{collection}: {info.points_count} vectors")
        except Exception as e:
            print(f"{collection}: {e}")

if __name__ == "__main__":
    main()
```

### 3.3 Run Ingestion

```bash
# Install dependencies
pip install sentence-transformers qdrant-client

# Run ingestion
python3 /root/scripts/ingest_knowledge.py

# Verify
curl "http://localhost:6333/collections/rugs_protocol" | jq .result.points_count
```

---

## Phase 4: n8n Workflows

### 4.1 RAG Query Workflow

Create in n8n UI:

**Trigger:** Webhook (GET `/webhook/rag/query`)

**Flow:**
1. HTTP Request node → Parse query from `?q=...`
2. HTTP Request node → Embed query via local model OR OpenAI
3. Qdrant node → Search `rugs_protocol` collection
4. Code node → Format results
5. Respond to Webhook → Return JSON

### 4.2 WebSocket Ingestion Workflow

**Trigger:** RabbitMQ Trigger (queue: `websocket_events`)

**Flow:**
1. RabbitMQ Trigger → Receive batch
2. Loop Over Items → Process each event
3. Code node → Generate embedding text from event template
4. HTTP Request → Embed via local/OpenAI
5. Parallel branches:
   - Qdrant Insert → Vector storage
   - Postgres Execute → TimescaleDB insert
6. Error handling → Dead-letter queue

### 4.3 MCP Server Workflow

**Trigger:** MCP Server Trigger

**Tools to expose:**
- `query_protocol` → Search WEBSOCKET_EVENTS_SPEC
- `query_rl_design` → Search RL observation/action docs
- `get_event_stats` → TimescaleDB aggregates
- `recent_events` → Last N events from TimescaleDB

---

## Phase 5: Socket.IO Bridge

### 5.1 Bridge Service

Create `/root/socketio-bridge/`:

```javascript
// index.js - Socket.IO to RabbitMQ bridge
const { io } = require('socket.io-client');
const amqp = require('amqplib');

const RUGS_URL = 'https://backend.rugs.fun?frontend-version=1.0';
const RABBITMQ_URL = 'amqp://n8n_rabbit:PASSWORD@localhost:5672/n8n';
const QUEUE = 'websocket_events';
const BATCH_SIZE = 50;
const FLUSH_INTERVAL = 5000;

let buffer = [];
let channel;

async function connectRabbitMQ() {
  const conn = await amqp.connect(RABBITMQ_URL);
  channel = await conn.createChannel();
  await channel.assertQueue(QUEUE, { durable: true });
  console.log('RabbitMQ connected');
}

function flushBuffer() {
  if (buffer.length === 0) return;

  const batch = buffer.splice(0, buffer.length);
  channel.sendToQueue(QUEUE, Buffer.from(JSON.stringify(batch)), {
    persistent: true
  });
  console.log(`Flushed ${batch.length} events`);
}

async function main() {
  await connectRabbitMQ();

  const socket = io(RUGS_URL, {
    transports: ['websocket']
  });

  socket.on('connect', () => console.log('Socket.IO connected'));

  socket.onAny((event, ...args) => {
    buffer.push({
      event,
      data: args,
      timestamp: Date.now()
    });

    if (buffer.length >= BATCH_SIZE) {
      flushBuffer();
    }
  });

  setInterval(flushBuffer, FLUSH_INTERVAL);
}

main().catch(console.error);
```

### 5.2 Docker Container

```dockerfile
# Dockerfile
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
CMD ["node", "index.js"]
```

```yaml
# Add to /root/rag-stack/docker-compose.yml
  socketio-bridge:
    build: /root/socketio-bridge
    container_name: socketio-bridge
    restart: unless-stopped
    depends_on:
      - rabbitmq
    networks:
      - n8n_default
```

---

## Phase 6: Verification

### 6.1 Test RAG Query

```bash
# Query the protocol knowledge
curl "http://localhost:5678/webhook/rag/query?q=gameStateUpdate%20fields"
```

### 6.2 Test MCP Tools

```bash
# From Claude Code
claude mcp add rugs-rag http://72.62.160.2:5678/mcp
```

### 6.3 Verify Event Flow

```bash
# Check RabbitMQ queue depth
curl -u n8n_rabbit:PASSWORD "http://localhost:15672/api/queues/n8n/websocket_events" | jq .messages

# Check TimescaleDB event count
docker exec timescaledb psql -U n8n_tsdb -d rugs_analytics -c "SELECT COUNT(*) FROM websocket_events"
```

---

## Resource Budget

| Component | RAM | Disk | Notes |
|-----------|-----|------|-------|
| Existing (n8n, postgres) | ~1.5 GB | 3 GB | Running |
| Qdrant | ~500 MB | 2 GB | For ~10K vectors |
| RabbitMQ | ~256 MB | 500 MB | Running |
| TimescaleDB | ~512 MB | 5 GB | Running |
| Socket.IO Bridge | ~100 MB | 50 MB | New |
| **Total** | **~2.9 GB** | **~11 GB** | Within limits |

VPS has 3.8 GB RAM, 32 GB disk free. **Fits comfortably.**

---

## Migration Checklist

### Phase 0: Documentation Export (CRITICAL)
- [ ] Verify all docs created (SYSTEM_ARCHITECTURE, RESTORATION_GUIDE, AUTONOMOUS_OPS)
- [ ] Upload docs to VPS (`rsync -avz ~/Desktop/VPS/docs/ hostinger-vps:/root/docs/`)
- [ ] Export Claude Code config (mcp list, plugins)
- [ ] Create backup bundle with SSH keys
- [ ] Copy backup-bundle.tar.gz to USB/cloud
- [ ] Verify VPS accessible from public internet

### Phase 1: Knowledge Export (Local)
- [ ] Create `~/Desktop/VPS/knowledge-export/`
- [ ] Copy rugipedia
- [ ] Copy rl-design
- [ ] Extract RAG SUPERPACK docs
- [ ] Copy game recordings

### Phase 2: Upload to VPS
- [ ] rsync knowledge to `/root/knowledge/`
- [ ] Verify file counts

### Phase 3: Qdrant Ingestion
- [ ] Create collections (rugs_protocol, rl_design, external_docs)
- [ ] Install Python dependencies
- [ ] Run ingest_knowledge.py
- [ ] Verify vector counts

### Phase 4: n8n Workflows
- [ ] Create RAG query workflow
- [ ] Create WebSocket ingestion workflow
- [ ] Create MCP server workflow
- [ ] Test each workflow

### Phase 5: Socket.IO Bridge
- [ ] Create bridge service
- [ ] Build Docker container
- [ ] Add to docker-compose.yml
- [ ] Deploy and verify

### Phase 6: Verification
- [ ] Test RAG queries
- [ ] Test MCP tools from Claude
- [ ] Verify event flow end-to-end

---

## Timeline Estimate

| Phase | Duration | Dependencies |
|-------|----------|--------------|
| Phase 1 | 30 min | Local machine |
| Phase 2 | 15 min | Network |
| Phase 3 | 1 hour | VPS |
| Phase 4 | 2 hours | n8n UI |
| Phase 5 | 1 hour | VPS |
| Phase 6 | 30 min | All above |
| **Total** | **~5 hours** | |

---

*Plan created: 2026-01-01*
*Ready for execution after laptop migration*
