"""MCP tool implementations for rugs.fun knowledge queries."""

from typing import Optional

from .rag_client import rag_client


async def search_rugs_knowledge(
    query: str,
    collections: Optional[list[str]] = None,
    limit: int = 5
) -> str:
    """
    Semantic search across rugs.fun knowledge base.

    Use this tool to find information about:
    - Game mechanics and rules
    - WebSocket events and their structure
    - Trading strategies and price dynamics
    - Provably fair verification
    - Any rugs.fun protocol documentation

    Args:
        query: Natural language search query describing what you want to know
        collections: Optional filter - ["rugs_protocol", "external_docs", "rl_design"]
        limit: Maximum results to return (1-10)

    Returns:
        Formatted search results with source attribution
    """
    try:
        results = await rag_client.search(
            query=query,
            collections=collections,
            limit=min(limit, 10)
        )

        if not results:
            return f"No results found for: {query}\n\nTry rephrasing your query or broadening the search."

        output = [f"## Search Results for: {query}\n"]

        for i, result in enumerate(results, 1):
            score = result.get("score", 0)
            source = result.get("source", "unknown")
            text = result.get("text", "")
            collection = result.get("collection", "")

            output.append(f"### Result {i} (relevance: {score:.2f})")
            output.append(f"**Source:** `{source}` ({collection})\n")
            output.append(text)
            output.append("\n---\n")

        return "\n".join(output)

    except Exception as e:
        return f"Error searching knowledge base: {str(e)}"


async def get_game_event_schema(event_name: str) -> str:
    """
    Get the schema and structure for a specific rugs.fun WebSocket event.

    Common events:
    - gameStateUpdate: Main game state with players, prices, active status
    - playerBet: When a player places a bet
    - playerCashout: When a player cashes out
    - gameEnded: Game completion with final results

    Args:
        event_name: Name of the event (e.g., "gameStateUpdate", "playerBet")

    Returns:
        Event schema, field definitions, and example payloads
    """
    # Search specifically for event documentation
    query = f"{event_name} event structure fields schema WebSocket"

    try:
        results = await rag_client.search(
            query=query,
            collections=["rugs_protocol"],
            limit=3
        )

        if not results:
            return f"No schema found for event: {event_name}\n\nAvailable events: gameStateUpdate, playerBet, playerCashout, gameEnded"

        output = [f"## Event Schema: {event_name}\n"]

        for result in results:
            source = result.get("source", "unknown")
            text = result.get("text", "")
            output.append(f"**Source:** `{source}`\n")
            output.append(text)
            output.append("\n---\n")

        return "\n".join(output)

    except Exception as e:
        return f"Error fetching event schema: {str(e)}"


async def get_trading_mechanics(topic: str) -> str:
    """
    Get detailed information about rugs.fun trading mechanics.

    Topics:
    - price_curve: How prices change over time, tick mechanics
    - volatility: Price volatility mechanics and formulas
    - rug_conditions: What triggers a rug, detection methods
    - provably_fair: Verification system, server seeds, hashing
    - betting: Bet placement, cashout mechanics, multipliers
    - game_lifecycle: Game phases, timing, state transitions

    Args:
        topic: The trading mechanic topic to query

    Returns:
        Detailed explanation with formulas and examples
    """
    topic_queries = {
        "price_curve": "price curve tick mechanics price movement calculation",
        "volatility": "volatility price swings calculation formula v3",
        "rug_conditions": "rug trigger conditions detection game end",
        "provably_fair": "provably fair server seed hash verification",
        "betting": "bet placement cashout multiplier calculation",
        "game_lifecycle": "game state lifecycle phases active ended"
    }

    search_query = topic_queries.get(
        topic.lower(),
        f"{topic} mechanics rugs trading"
    )

    try:
        results = await rag_client.search(
            query=search_query,
            collections=["rugs_protocol", "rl_design"],
            limit=5
        )

        if not results:
            available = ", ".join(topic_queries.keys())
            return f"No information found for topic: {topic}\n\nAvailable topics: {available}"

        output = [f"## Trading Mechanics: {topic}\n"]

        for result in results:
            source = result.get("source", "unknown")
            text = result.get("text", "")
            score = result.get("score", 0)

            output.append(f"**Source:** `{source}` (relevance: {score:.2f})\n")
            output.append(text)
            output.append("\n---\n")

        return "\n".join(output)

    except Exception as e:
        return f"Error fetching trading mechanics: {str(e)}"


async def list_knowledge_sources(collection: Optional[str] = None) -> str:
    """
    List all available documentation sources in the knowledge base.

    Use this to discover what documentation is available before searching.

    Args:
        collection: Optional filter - "rugs_protocol", "external_docs", or "rl_design"

    Returns:
        List of indexed sources organized by collection
    """
    try:
        collections = await rag_client.get_collections()

        if collection:
            # Filter to specific collection
            collections = [c for c in collections if c.get("name") == collection]
            if not collections:
                return f"Collection not found: {collection}\n\nAvailable: rugs_protocol, external_docs, rl_design"

        output = ["## Knowledge Base Sources\n"]

        for coll in collections:
            name = coll.get("name", "unknown")
            points = coll.get("points_count", 0)
            status = coll.get("status", "unknown")

            output.append(f"### {name}")
            output.append(f"- **Vectors:** {points}")
            output.append(f"- **Status:** {status}\n")

            # Get sources for this collection
            try:
                sources = await rag_client.get_sources(name)
                if sources:
                    output.append("**Sources:**")
                    for src in sources[:20]:  # Limit to 20
                        path = src.get("path", "unknown")
                        chunks = src.get("chunk_count", 0)
                        output.append(f"- `{path}` ({chunks} chunks)")

                    if len(sources) > 20:
                        output.append(f"- ... and {len(sources) - 20} more")
            except Exception:
                output.append("- (sources unavailable)")

            output.append("")

        return "\n".join(output)

    except Exception as e:
        return f"Error listing sources: {str(e)}"
