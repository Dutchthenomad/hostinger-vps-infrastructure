# Rugs Expert MCP Server Design

**Date:** 2026-01-04
**Status:** Approved
**Purpose:** RAG-backed MCP server providing grounded rugs.fun knowledge to Claude Code projects

## Problem Statement

Development agents working on VECTRA-PLAYER hallucinate game mechanics without access to authoritative rugs.fun documentation. The knowledge exists in Qdrant (1,502 vectors across 3 collections) but isn't accessible to Claude Code projects.

## Solution

VPS-hosted MCP server using Anthropic Agent SDK that wraps the existing RAG API, exposing semantic search tools via SSE transport.

## Architecture

```
┌─────────────────┐     SSE      ┌──────────────────┐     HTTP     ┌─────────────┐
│  Claude Code    │◄────────────►│  MCP Server      │◄────────────►│  RAG API    │
│  (any project)  │    :8001     │  (Agent SDK)     │    :8000     │  (FastAPI)  │
└─────────────────┘              └──────────────────┘              └─────────────┘
                                         │
                                         ▼
                                 ┌─────────────┐
                                 │   Qdrant    │
                                 │   :6333     │
                                 └─────────────┘
```

## MCP Tools

### 1. `search_rugs_knowledge`
Semantic search across all knowledge collections.

**Parameters:**
- `query` (string, required): Natural language search query
- `collections` (array, optional): Filter to specific collections. Default: all
- `limit` (int, optional): Max results. Default: 5

**Returns:** Array of relevant text chunks with source attribution and relevance scores.

### 2. `get_game_event_schema`
Lookup specific WebSocket event structure and fields.

**Parameters:**
- `event_name` (string, required): Event type (e.g., "gameStateUpdate", "playerBet")

**Returns:** Event schema, field definitions, example payloads.

### 3. `get_trading_mechanics`
Query price curves, volatility mechanics, and rug conditions.

**Parameters:**
- `topic` (string, required): Specific mechanic (e.g., "price_curve", "volatility", "rug_conditions")

**Returns:** Detailed explanation with formulas and examples.

### 4. `list_knowledge_sources`
Browse available documentation in the knowledge base.

**Parameters:**
- `collection` (string, optional): Filter to specific collection

**Returns:** List of indexed sources with chunk counts.

## Collections

| Collection | Content | Vectors |
|------------|---------|---------|
| `rugs_protocol` | Core game mechanics, events, provably fair | 401 |
| `external_docs` | External documentation, guides | 1,061 |
| `rl_design` | RL training design docs | 40 |

## Deployment

**Location:** VPS (72.62.160.2)
**Port:** 8001 (MCP SSE)
**Transport:** Server-Sent Events
**Container:** `rugs-mcp` (Docker)

### Client Connection
```bash
claude mcp add rugs-expert --transport sse --url http://72.62.160.2:8001/sse
```

### Environment Variables
```
RAG_API_URL=http://localhost:8000
MCP_PORT=8001
```

## Implementation Stack

- **Runtime:** Python 3.11
- **Framework:** Anthropic Agent SDK (mcp server mode)
- **HTTP Client:** httpx (async)
- **Deployment:** Docker container on VPS

## File Structure

```
rugs-mcp/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── src/
    ├── __init__.py
    ├── server.py          # MCP server entry point
    ├── tools.py           # Tool implementations
    └── rag_client.py      # RAG API client
```

## Success Criteria

1. Claude Code projects can connect via `claude mcp add`
2. `search_rugs_knowledge` returns relevant, grounded results
3. rugs-expert agent stops hallucinating game mechanics
4. < 500ms response time for typical queries
