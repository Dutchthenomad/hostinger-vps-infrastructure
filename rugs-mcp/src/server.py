"""
Rugs Expert MCP Server

Provides RAG-backed knowledge tools for rugs.fun game mechanics.
Designed to be called from Claude Code projects via SSE transport.
"""

import asyncio
import os
from typing import Optional

from dotenv import load_dotenv
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import Tool, TextContent
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import JSONResponse

from .tools import (
    search_rugs_knowledge,
    get_game_event_schema,
    get_trading_mechanics,
    list_knowledge_sources
)
from .rag_client import rag_client

load_dotenv()

# Create MCP server
server = Server("rugs-expert")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="search_rugs_knowledge",
            description=(
                "Semantic search across rugs.fun knowledge base. "
                "Use this to find information about game mechanics, WebSocket events, "
                "trading strategies, provably fair verification, and protocol documentation."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Natural language search query"
                    },
                    "collections": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional: filter to specific collections (rugs_protocol, external_docs, rl_design)"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum results (1-10, default 5)",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_game_event_schema",
            description=(
                "Get the schema and structure for a rugs.fun WebSocket event. "
                "Use for: gameStateUpdate, playerBet, playerCashout, gameEnded"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "event_name": {
                        "type": "string",
                        "description": "Event name (e.g., gameStateUpdate, playerBet)"
                    }
                },
                "required": ["event_name"]
            }
        ),
        Tool(
            name="get_trading_mechanics",
            description=(
                "Get detailed information about rugs.fun trading mechanics. "
                "Topics: price_curve, volatility, rug_conditions, provably_fair, betting, game_lifecycle"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "Trading mechanic topic to query"
                    }
                },
                "required": ["topic"]
            }
        ),
        Tool(
            name="list_knowledge_sources",
            description=(
                "List all available documentation sources in the knowledge base. "
                "Use to discover what documentation is indexed before searching."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "collection": {
                        "type": "string",
                        "description": "Optional: filter to specific collection"
                    }
                }
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Execute a tool and return results."""
    try:
        if name == "search_rugs_knowledge":
            result = await search_rugs_knowledge(
                query=arguments["query"],
                collections=arguments.get("collections"),
                limit=arguments.get("limit", 5)
            )
        elif name == "get_game_event_schema":
            result = await get_game_event_schema(
                event_name=arguments["event_name"]
            )
        elif name == "get_trading_mechanics":
            result = await get_trading_mechanics(
                topic=arguments["topic"]
            )
        elif name == "list_knowledge_sources":
            result = await list_knowledge_sources(
                collection=arguments.get("collection")
            )
        else:
            result = f"Unknown tool: {name}"

        return [TextContent(type="text", text=result)]

    except Exception as e:
        return [TextContent(type="text", text=f"Error executing {name}: {str(e)}")]


# Health check endpoint
async def health_check(request):
    """Health check endpoint."""
    try:
        health = await rag_client.health_check()
        return JSONResponse({
            "status": "healthy",
            "mcp_server": "rugs-expert",
            "rag_api": health
        })
    except Exception as e:
        return JSONResponse({
            "status": "degraded",
            "mcp_server": "rugs-expert",
            "error": str(e)
        }, status_code=503)


# SSE endpoint handler
async def handle_sse(request):
    """Handle SSE connections from MCP clients."""
    transport = SseServerTransport("/messages/")
    async with transport.connect_sse(
        request.scope,
        request.receive,
        request._send
    ) as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


# Create Starlette app
app = Starlette(
    routes=[
        Route("/health", health_check),
        Route("/sse", handle_sse),
    ]
)


def main():
    """Run the MCP server."""
    import uvicorn

    host = os.getenv("MCP_HOST", "0.0.0.0")
    port = int(os.getenv("MCP_PORT", "8001"))

    print(f"Starting Rugs Expert MCP Server on {host}:{port}")
    print(f"RAG API: {os.getenv('RAG_API_URL', 'http://localhost:8000')}")
    print(f"SSE endpoint: http://{host}:{port}/sse")
    print(f"Health check: http://{host}:{port}/health")

    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
