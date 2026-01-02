# System Architecture - Complete Documentation

**Created:** 2026-01-01
**Purpose:** Full system documentation for restoration on new PC

---

## Overview

This document describes the complete architecture of the rugs.fun quantitative analysis and trading system. It covers:
- Local development environment
- VPS infrastructure
- RAG knowledge system
- Project relationships

---

## 1. VPS Infrastructure (srv1216617.hstgr.cloud)

### Connection Details

```
Host: 72.62.160.2
SSH: ssh root@72.62.160.2 -i ~/.ssh/hostinger_vps
Alias: hostinger-vps (configured in ~/.ssh/config)
```

### Running Services

| Service | Port | Container | Purpose |
|---------|------|-----------|---------|
| n8n | 5678 | n8n | Workflow automation |
| n8n-postgres | 5432 | n8n-postgres | n8n metadata |
| Qdrant | 6333 | qdrant | Vector database |
| RabbitMQ | 5672, 15672 | rabbitmq | Message queue |
| TimescaleDB | 5433 | timescaledb | Time-series analytics |

### Docker Compose Location

```
/root/rag-stack/docker-compose.yml
```

### Service Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    VPS (72.62.160.2)                        │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │    n8n      │    │   Qdrant    │    │ TimescaleDB │     │
│  │   :5678     │    │   :6333     │    │   :5433     │     │
│  │  Workflows  │    │   Vectors   │    │ Time-series │     │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘     │
│         │                  │                  │             │
│         └──────────────────┼──────────────────┘             │
│                            │                                │
│  ┌─────────────┐    ┌──────┴──────┐                        │
│  │  RabbitMQ   │◄───│ Socket.IO   │ (NOT YET BUILT)        │
│  │   :5672     │    │   Bridge    │                        │
│  │   Queue     │    │             │                        │
│  └─────────────┘    └─────────────┘                        │
│                            ▲                                │
└────────────────────────────┼────────────────────────────────┘
                             │ WebSocket
                    ┌────────┴────────┐
                    │  rugs.fun API   │
                    │ backend.rugs.fun│
                    └─────────────────┘
```

---

## 2. Local Projects Structure

### Project Locations

| Project | Path | Purpose |
|---------|------|---------|
| claude-flow | `/home/nomad/Desktop/claude-flow` | Development workflow + RAG pipeline |
| REPLAYER | `/home/nomad/Desktop/REPLAYER` | Game replay/live viewer |
| rugs-rl-bot | `/home/nomad/Desktop/rugs-rl-bot` | RL trading bot |
| CV-BOILER-PLATE-FORK | `/home/nomad/Desktop/CV-BOILER-PLATE-FORK` | YOLO object detection |
| VPS | `/home/nomad/Desktop/VPS` | VPS configuration + docs |
| rugs_recordings | `/home/nomad/rugs_recordings` | Game recording archive |

### Project Relationships

```
                    ┌─────────────────┐
                    │   claude-flow   │
                    │ (methodology +  │
                    │    knowledge)   │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
     ┌────────────┐  ┌────────────┐  ┌────────────┐
     │  REPLAYER  │  │ rugs-rl-bot│  │ CV-YOLO    │
     │  (viewer)  │  │   (agent)  │  │ (vision)   │
     └──────┬─────┘  └──────┬─────┘  └────────────┘
            │               │
            └───────┬───────┘
                    │
            ┌───────▼───────┐
            │rugs_recordings│
            │  (929 games)  │
            └───────────────┘
```

---

## 3. Knowledge Base Structure

### Location
```
/home/nomad/Desktop/claude-flow/knowledge/
```

### Contents

```
knowledge/
├── rugipedia/              # 824 KB, 28 files (CANONICAL)
│   ├── canon/
│   │   ├── WEBSOCKET_EVENTS_SPEC.md    # Master protocol doc
│   │   ├── CONNECTION_DIAGRAM.md       # Architecture diagram
│   │   └── PROVABLY_FAIR_VERIFICATION.md
│   ├── blockchain/         # Forensic audits
│   ├── game-modes/         # BBC, Candleflip, FAQ
│   ├── generated/          # Indexes, FIELD_DICTIONARY
│   └── archive/            # Q files, connection guides
├── rl-design/              # 52 KB, 5 files
│   ├── observation-space-design.md
│   ├── action-space-design.md
│   └── implementation-plan.md
└── RAG SUPERPACK/          # 1.7 GB (external repos)
    ├── RAG_KNOWLEDGE_SOURCES.md
    ├── RISK_MANAGEMENT_SOURCES.md
    └── [37 cloned repositories]
```

---

## 4. RAG Pipeline

### Local Pipeline (claude-flow/rag-pipeline/)

```
rag-pipeline/
├── config.py               # Configuration
├── ingestion/
│   ├── chunker.py          # Text chunking
│   └── ingest.py           # Main ingestion
├── retrieval/
│   └── retrieve.py         # Query interface
└── storage/
    └── store.py            # Vector storage
```

### VPS Pipeline (Target State)

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Claude     │────▶│    n8n       │────▶│   Qdrant     │
│   (MCP)      │     │  Workflows   │     │   Vectors    │
└──────────────┘     └──────────────┘     └──────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │ TimescaleDB  │
                     │  (events)    │
                     └──────────────┘
```

---

## 5. Claude Code Configuration

### MCP Servers (Required)

```bash
# Add after restoration
claude mcp add rugs-rag http://72.62.160.2:5678/mcp
```

### SSH Config (~/.ssh/config)

```
Host hostinger-vps
    HostName 72.62.160.2
    User root
    IdentityFile ~/.ssh/hostinger_vps
    StrictHostKeyChecking no
```

### Plugins (claude-flow)

```
~/.claude/plugins/claude-flow -> /home/nomad/Desktop/claude-flow/.claude-plugin
```

---

## 6. Game Recording Archive

### Location
```
/home/nomad/rugs_recordings/
```

### Format
- JSONL files (one event per line)
- Each file = one game session
- ~929 files, ~401 MB total

### Event Structure
```json
{
  "event": "gameStateUpdate",
  "data": {...},
  "timestamp": 1735689600000
}
```

---

## 7. Critical Files Reference

### CANONICAL Protocol Spec
```
/home/nomad/Desktop/claude-flow/knowledge/rugipedia/canon/WEBSOCKET_EVENTS_SPEC.md
```

### VPS Credentials
```
/home/nomad/Desktop/VPS/CREDENTIALS.md  (DO NOT COMMIT)
```

### SSH Key
```
~/.ssh/hostinger_vps
```

### Migration Plan
```
/home/nomad/Desktop/VPS/docs/RAG_MIGRATION_PLAN.md
```

---

## 8. Data Flow (Target State)

```
┌─────────────────────────────────────────────────────────────────┐
│                        LIVE DATA FLOW                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  rugs.fun ──WebSocket──▶ Socket.IO Bridge ──▶ RabbitMQ         │
│                                                    │            │
│                                          ┌─────────┴─────────┐  │
│                                          ▼                   ▼  │
│                                     TimescaleDB          Qdrant │
│                                     (raw events)      (vectors) │
│                                          │                   │  │
│                                          └─────────┬─────────┘  │
│                                                    │            │
│                                               n8n MCP           │
│                                                    │            │
│                                            Claude Code          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 9. Credentials Summary

**See:** `/home/nomad/Desktop/VPS/CREDENTIALS.md`

| Service | Location | Notes |
|---------|----------|-------|
| VPS SSH | ~/.ssh/hostinger_vps | Private key |
| n8n | VPS:5678 | Basic auth |
| Qdrant | VPS:6333 | No auth (local only) |
| RabbitMQ | VPS:5672 | See CREDENTIALS.md |
| TimescaleDB | VPS:5433 | See CREDENTIALS.md |

---

*Document created: 2026-01-01*
*For restoration on new PC, see: NEW_PC_RESTORATION_GUIDE.md*
