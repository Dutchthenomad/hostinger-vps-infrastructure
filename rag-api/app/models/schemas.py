from pydantic import BaseModel, Field
from datetime import datetime


# Search
class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    collections: list[str] | None = None
    limit: int = Field(default=10, ge=1, le=100)
    score_threshold: float = Field(default=0.3, ge=0.0, le=1.0)
    source_filter: str | None = None


class SearchResult(BaseModel):
    id: str
    text: str
    source: str
    chunk_index: int
    score: float
    collection: str


class SearchResponse(BaseModel):
    results: list[SearchResult]
    query: str
    session_id: str | None
    total_results: int


# Collections
class CollectionStats(BaseModel):
    name: str
    points_count: int
    status: str
    vector_size: int


class CollectionsResponse(BaseModel):
    collections: list[CollectionStats]


class SourceInfo(BaseModel):
    path: str
    chunk_count: int


class SourcesResponse(BaseModel):
    collection: str
    sources: list[SourceInfo]


class DocumentChunk(BaseModel):
    id: str
    text: str
    source: str
    chunk_index: int


class DocumentsResponse(BaseModel):
    collection: str
    source: str
    documents: list[DocumentChunk]


# Session
class QueryHistoryItem(BaseModel):
    id: int
    query: str
    timestamp: datetime
    result_count: int
    collections: list[str]


class SessionResponse(BaseModel):
    session_id: str
    created_at: datetime
    queries: list[QueryHistoryItem]


class HistoryResponse(BaseModel):
    session_id: str
    queries: list[QueryHistoryItem]


# Health
class HealthResponse(BaseModel):
    status: str
    qdrant_connected: bool
    collections_available: int
    embedding_model: str
