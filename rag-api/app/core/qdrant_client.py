from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchText

from app.config import get_settings


class RAGQdrantClient:
    def __init__(self):
        settings = get_settings()
        self.client = QdrantClient(
            host=settings.qdrant_host,
            port=settings.qdrant_port
        )
        self.collections = settings.collections

    def search(
        self,
        query_vector: list[float],
        collections: list[str] | None = None,
        limit: int = 10,
        score_threshold: float = 0.3,
        source_filter: str | None = None
    ) -> list[dict]:
        collections = collections or self.collections
        all_results = []

        for collection in collections:
            if collection not in self.collections:
                continue

            filter_condition = None
            if source_filter:
                filter_condition = Filter(
                    must=[FieldCondition(
                        key="source",
                        match=MatchText(text=source_filter)
                    )]
                )

            results = self.client.query_points(
                collection_name=collection,
                query=query_vector,
                limit=limit,
                score_threshold=score_threshold,
                query_filter=filter_condition
            )

            for r in results.points:
                all_results.append({
                    "id": str(r.id),
                    "score": r.score,
                    "text": r.payload.get("text", ""),
                    "source": r.payload.get("source", ""),
                    "chunk_index": r.payload.get("chunk_index", 0),
                    "collection": collection
                })

        all_results.sort(key=lambda x: x["score"], reverse=True)
        return all_results[:limit]

    def get_collection_stats(self) -> list[dict]:
        stats = []
        for name in self.collections:
            try:
                info = self.client.get_collection(name)
                stats.append({
                    "name": name,
                    "points_count": info.points_count,
                    "status": str(info.status),
                    "vector_size": info.config.params.vectors.size
                })
            except Exception:
                continue
        return stats

    def get_unique_sources(self, collection: str) -> list[dict]:
        if collection not in self.collections:
            return []

        sources: dict[str, int] = {}
        offset = None

        while True:
            results, next_offset = self.client.scroll(
                collection_name=collection,
                limit=100,
                offset=offset,
                with_payload=["source"]
            )

            for point in results:
                source = point.payload.get("source", "unknown")
                sources[source] = sources.get(source, 0) + 1

            if next_offset is None:
                break
            offset = next_offset

        return [{"path": k, "chunk_count": v} for k, v in sorted(sources.items())]

    def get_documents_by_source(
        self,
        collection: str,
        source: str,
        limit: int = 50
    ) -> list[dict]:
        if collection not in self.collections:
            return []

        results, _ = self.client.scroll(
            collection_name=collection,
            limit=limit,
            scroll_filter=Filter(
                must=[FieldCondition(
                    key="source",
                    match=MatchText(text=source)
                )]
            ),
            with_payload=True
        )

        docs = []
        for point in results:
            docs.append({
                "id": str(point.id),
                "text": point.payload.get("text", ""),
                "source": point.payload.get("source", ""),
                "chunk_index": point.payload.get("chunk_index", 0)
            })

        docs.sort(key=lambda x: x["chunk_index"])
        return docs
