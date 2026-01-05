"""RAG API client for querying the knowledge base."""

import os
from typing import Optional

import httpx

RAG_API_URL = os.getenv("RAG_API_URL", "http://localhost:8000")


class RAGClient:
    """Async client for the RAG Knowledge API."""

    def __init__(self, base_url: str = RAG_API_URL):
        self.base_url = base_url.rstrip("/")
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=30.0
            )
        return self._client

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None

    async def health_check(self) -> dict:
        """Check RAG API health."""
        client = await self._get_client()
        response = await client.get("/api/health")
        response.raise_for_status()
        return response.json()

    async def search(
        self,
        query: str,
        collections: Optional[list[str]] = None,
        limit: int = 5,
        score_threshold: float = 0.3
    ) -> list[dict]:
        """
        Semantic search across knowledge collections.

        Args:
            query: Natural language search query
            collections: Optional list of collections to search
            limit: Maximum number of results
            score_threshold: Minimum relevance score

        Returns:
            List of search results with text, source, and score
        """
        client = await self._get_client()

        payload = {
            "query": query,
            "limit": limit,
            "score_threshold": score_threshold
        }
        if collections:
            payload["collections"] = collections

        response = await client.post("/api/search", json=payload)
        response.raise_for_status()

        data = response.json()
        return data.get("results", [])

    async def get_collections(self) -> list[dict]:
        """Get all available collections with stats."""
        client = await self._get_client()
        response = await client.get("/api/collections")
        response.raise_for_status()

        data = response.json()
        return data.get("collections", [])

    async def get_sources(self, collection: str) -> list[dict]:
        """Get all sources in a collection."""
        client = await self._get_client()
        response = await client.get(f"/api/collections/{collection}/sources")
        response.raise_for_status()

        data = response.json()
        return data.get("sources", [])


# Global client instance
rag_client = RAGClient()
