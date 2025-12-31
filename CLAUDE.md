# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains two components:
1. **n8n + Postgres Docker deployment** for Hostinger VPS (Docker Manager)
2. **n8n-nodes-hostinger-api** - A community n8n node for Hostinger API integration

## Commands

### n8n Node Development (api-n8n-node/)

```bash
cd api-n8n-node

# Install dependencies
npm install

# Build the node
npm run build

# Watch mode during development
npm run build:watch

# Lint code
npm run lint
npm run lint:fix

# Development mode (auto-reload)
npm run dev

# Release
npm run release
```

### Docker Deployment

The `docker-compose.yml` and `.env` files are meant for manual deployment via Hostinger's Docker Manager UI, not command-line Docker. See `SETUP_N8N_HOSTINGER.md` for deployment steps.

## Architecture

### n8n Community Node Structure

```
api-n8n-node/
├── credentials/
│   └── HostingerApi.credentials.ts    # API token authentication
├── nodes/
│   └── hostingerApi/
│       ├── HostingerApi.node.ts       # Main node implementation (~1500 lines)
│       ├── HostingerApi.node.json     # Node metadata
│       └── hostingerLogo.*.svg        # Node icons
```

### Node Implementation Pattern

The `HostingerApi.node.ts` uses the standard n8n node pattern:
- **Resources**: VPS, Domain, DNS, Billing, Reach (email marketing), Docker Manager, Firewall, etc.
- **Operations**: CRUD operations for each resource
- **Execution flow**:
  1. Parse resource and operation from parameters
  2. Build request body from individual fields (not raw JSON for most operations)
  3. Construct API endpoint via switch statement
  4. Execute HTTP request with Bearer token authentication
  5. Return response or handle errors with `continueOnFail` support

### Key Implementation Details

- API base URL: `https://developers.hostinger.com`
- Authentication: Bearer token via `httpRequestWithAuthentication`
- The node is marked `usableAsTool: true` for AI agent compatibility
- Extensive use of `displayOptions.show` for conditional field visibility
- Most operations build request bodies from individual form fields rather than raw JSON

## Hostinger API Resources

The node covers these API areas:
- **VPS**: Server management, metrics, hostname, passwords, nameservers, recovery, snapshots
- **VPS Docker**: Project lifecycle (create/start/stop/restart/update/delete), container listing, logs
- **VPS Firewall**: Rules, activation, sync
- **VPS Backups/Snapshots**: CRUD operations
- **Domain**: Availability check, purchase, lock, privacy protection, nameservers
- **DNS**: Zone management, snapshots
- **Billing**: Catalog, payment methods, subscriptions
- **Reach**: Email contacts and segments

## Docker Stacks

### n8n Stack (Core)

- **n8n**: Workflow automation (port 5678)
- **PostgreSQL 16**: Persistent storage for n8n workflows and credentials
- **Volumes**: `n8n_n8n_data`, `n8n_n8n_pgdata`
- **Network**: `n8n_default` (bridge)

### RAG Stack (Analytics Infrastructure)

Deployed via `/root/rag-stack/docker-compose.yml`:

- **Qdrant**: Vector database for RAG retrieval (ports 6333 HTTP, 6334 gRPC)
- **RabbitMQ**: Message queue for real-time event buffering (ports 5672 AMQP, 15672 Management)
- **TimescaleDB**: Time-series analytics database (port 5433)
- **Volumes**: `rag-stack_qdrant_data`, `rag-stack_rabbitmq_data`, `rag-stack_timescaledb_data`

**Purpose**: Store embeddings, buffer WebSocket events, and store time-series analytics for rugs.fun data.

---

## VPS Access & System Info

### SSH Access

```bash
# Connect to VPS (uses local SSH config)
ssh hostinger-vps

# SSH config location: ~/.ssh/config
# Key location: /home/nomad/Desktop/VPS/.ssh/hostinger_vps
```

| Property | Value |
|----------|-------|
| Hostname | srv1216617 |
| IP (Public) | 72.62.160.2 |
| IPv6 | 2a02:4780:2d:afd2::1 |
| Tailscale IP | 100.113.138.27 |
| SSH User | root |

### System Specs (Updated 2025-12-31)

| Resource | Value |
|----------|-------|
| OS | Ubuntu 24.04.3 LTS (Noble Numbat) |
| Kernel | 6.8.0-90-generic x86_64 |
| CPU Cores | 1 |
| RAM | 3.8 GB total (~2.7 GB available) |
| Disk | 48 GB (34% used, 32 GB free) |
| Swap | 2.0 GB |

### Running Services

| Service | Purpose |
|---------|---------|
| Docker | Container runtime (v29.1.3) |
| SSH | Remote access (port 22) |
| Tailscale | VPN mesh network |
| Monarx Agent | Security scanner |
| systemd-resolved | DNS resolution |

### Docker Containers (Current)

| Container | Image | Port | Status |
|-----------|-------|------|--------|
| n8n | n8nio/n8n:latest | 5678 | Running |
| n8n-postgres | postgres:16 | 5432 (internal) | Running |
| qdrant | qdrant/qdrant:latest | 6333, 6334 | Running |
| rabbitmq | rabbitmq:3-management | 5672, 15672 | Running (healthy) |
| timescaledb | timescale/timescaledb:latest-pg15 | 5433 | Running (healthy) |

### Exposed Ports

| Port | Service |
|------|---------|
| 22 | SSH |
| 5678 | n8n (HTTP) |
| 5672 | RabbitMQ (AMQP) |
| 6333 | Qdrant (HTTP API) |
| 6334 | Qdrant (gRPC) |
| 15672 | RabbitMQ (Management UI) |
| 5433 | TimescaleDB (PostgreSQL) |

### Access URLs

- **n8n UI**: http://72.62.160.2:5678
- **RabbitMQ Management**: http://72.62.160.2:15672
- **Qdrant Dashboard**: http://72.62.160.2:6333/dashboard
- **Tailscale n8n**: http://100.113.138.27:5678

### VPS Directory Structure

```
/root/
├── rag-stack/              # RAG infrastructure docker-compose
│   ├── docker-compose.yml
│   └── .env                # RabbitMQ/TimescaleDB credentials
├── projects/
│   ├── VECTRA-PLAYER/      # Cloned project
│   ├── claude-flow/        # Cloned project
│   └── RAG-INFRASTRUCTURE-PLAN.md
├── scripts/                # Utility scripts
└── .claude/                # Claude Code configuration
