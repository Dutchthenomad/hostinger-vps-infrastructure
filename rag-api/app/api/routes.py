from fastapi import APIRouter, Request, HTTPException, Cookie
from typing import Optional

from app.models.schemas import (
    SearchRequest, SearchResponse, SearchResult,
    CollectionsResponse, CollectionStats,
    SourcesResponse, SourceInfo,
    DocumentsResponse, DocumentChunk,
    SessionResponse, HistoryResponse, QueryHistoryItem,
    HealthResponse
)
from app.config import get_settings

router = APIRouter()


def get_qdrant(request: Request):
    return request.app.state.qdrant_client


def get_embeddings(request: Request):
    return request.app.state.embedding_service


def get_sessions(request: Request):
    return request.app.state.session_store


# Health
@router.get("/health", response_model=HealthResponse)
async def health_check(request: Request):
    qdrant = get_qdrant(request)
    embeddings = get_embeddings(request)
    settings = get_settings()

    try:
        stats = qdrant.get_collection_stats()
        qdrant_connected = True
        collections_count = len(stats)
    except Exception:
        qdrant_connected = False
        collections_count = 0

    return HealthResponse(
        status="healthy" if qdrant_connected else "degraded",
        qdrant_connected=qdrant_connected,
        collections_available=collections_count,
        embedding_model=settings.embedding_model
    )


# Search
@router.post("/search", response_model=SearchResponse)
async def search(
    request: Request,
    search_request: SearchRequest,
    session_id: Optional[str] = Cookie(default=None)
):
    qdrant = get_qdrant(request)
    embeddings = get_embeddings(request)
    sessions = get_sessions(request)

    # Generate embedding
    query_vector = embeddings.embed(search_request.query)

    # Search
    results = qdrant.search(
        query_vector=query_vector,
        collections=search_request.collections,
        limit=search_request.limit,
        score_threshold=search_request.score_threshold,
        source_filter=search_request.source_filter
    )

    # Track in session
    if session_id:
        sessions.add_query(
            session_id=session_id,
            query=search_request.query,
            result_count=len(results),
            collections=search_request.collections or get_settings().collections
        )

    return SearchResponse(
        results=[SearchResult(**r) for r in results],
        query=search_request.query,
        session_id=session_id,
        total_results=len(results)
    )


# Collections
@router.get("/collections", response_model=CollectionsResponse)
async def list_collections(request: Request):
    qdrant = get_qdrant(request)
    stats = qdrant.get_collection_stats()
    return CollectionsResponse(
        collections=[CollectionStats(**s) for s in stats]
    )


@router.get("/collections/{name}", response_model=CollectionStats)
async def get_collection(request: Request, name: str):
    qdrant = get_qdrant(request)
    stats = qdrant.get_collection_stats()

    for s in stats:
        if s["name"] == name:
            return CollectionStats(**s)

    raise HTTPException(status_code=404, detail=f"Collection '{name}' not found")


@router.get("/collections/{name}/sources", response_model=SourcesResponse)
async def list_sources(request: Request, name: str):
    qdrant = get_qdrant(request)
    settings = get_settings()

    if name not in settings.collections:
        raise HTTPException(status_code=404, detail=f"Collection '{name}' not found")

    sources = qdrant.get_unique_sources(name)
    return SourcesResponse(
        collection=name,
        sources=[SourceInfo(**s) for s in sources]
    )


@router.get("/collections/{name}/documents", response_model=DocumentsResponse)
async def get_documents(
    request: Request,
    name: str,
    source: str,
    limit: int = 50
):
    qdrant = get_qdrant(request)
    settings = get_settings()

    if name not in settings.collections:
        raise HTTPException(status_code=404, detail=f"Collection '{name}' not found")

    docs = qdrant.get_documents_by_source(name, source, limit)
    return DocumentsResponse(
        collection=name,
        source=source,
        documents=[DocumentChunk(**d) for d in docs]
    )


# Sessions
@router.post("/sessions")
async def create_session(request: Request):
    sessions = get_sessions(request)
    session_id = sessions.create_session()
    return {"session_id": session_id}


@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(request: Request, session_id: str):
    sessions = get_sessions(request)
    session = sessions.get_session(session_id)

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return SessionResponse(
        session_id=session.session_id,
        created_at=session.created_at,
        queries=[QueryHistoryItem(
            id=q.id,
            query=q.query,
            timestamp=q.timestamp,
            result_count=q.result_count,
            collections=q.collections
        ) for q in session.queries]
    )


@router.get("/sessions/{session_id}/history", response_model=HistoryResponse)
async def get_history(request: Request, session_id: str):
    sessions = get_sessions(request)
    history = sessions.get_history(session_id)

    return HistoryResponse(
        session_id=session_id,
        queries=[QueryHistoryItem(
            id=q.id,
            query=q.query,
            timestamp=q.timestamp,
            result_count=q.result_count,
            collections=q.collections
        ) for q in history]
    )


@router.delete("/sessions/{session_id}")
async def delete_session(request: Request, session_id: str):
    sessions = get_sessions(request)
    deleted = sessions.delete_session(session_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found")

    return {"status": "deleted", "session_id": session_id}
