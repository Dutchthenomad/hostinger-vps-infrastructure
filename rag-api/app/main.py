from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Form, Cookie
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from pathlib import Path

from app.api.routes import router as api_router
from app.core.embeddings import get_embedding_service
from app.core.qdrant_client import RAGQdrantClient
from app.core.session import SessionStore
from app.config import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Loading embedding model...")
    app.state.embedding_service = get_embedding_service()
    print("Connecting to Qdrant...")
    app.state.qdrant_client = RAGQdrantClient()
    app.state.session_store = SessionStore()
    print("RAG API ready!")
    yield
    # Shutdown
    print("Shutting down...")


app = FastAPI(
    title="RAG Knowledge API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files and templates
BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")

# API routes
app.include_router(api_router, prefix="/api")


# Web UI routes
@app.get("/", response_class=HTMLResponse)
async def index(request: Request, session_id: Optional[str] = Cookie(default=None)):
    sessions = request.app.state.session_store
    qdrant = request.app.state.qdrant_client

    # Get or create session
    session_id = sessions.get_or_create_session(session_id)
    collections = qdrant.get_collection_stats()

    response = templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "collections": collections,
            "session_id": session_id
        }
    )
    response.set_cookie("session_id", session_id, max_age=86400)
    return response


@app.get("/browse", response_class=HTMLResponse)
async def browse(request: Request):
    qdrant = request.app.state.qdrant_client
    collections = qdrant.get_collection_stats()

    return templates.TemplateResponse(
        "browse.html",
        {"request": request, "collections": collections}
    )


@app.get("/browse/{collection}", response_class=HTMLResponse)
async def browse_collection(request: Request, collection: str):
    qdrant = request.app.state.qdrant_client
    settings = get_settings()

    if collection not in settings.collections:
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": f"Collection '{collection}' not found"},
            status_code=404
        )

    collections = qdrant.get_collection_stats()
    sources = qdrant.get_unique_sources(collection)

    return templates.TemplateResponse(
        "browse.html",
        {
            "request": request,
            "collections": collections,
            "active_collection": collection,
            "sources": sources
        }
    )


# HTMX Partials
@app.post("/partials/results", response_class=HTMLResponse)
async def search_results(
    request: Request,
    query: str = Form(...),
    collections: list[str] = Form(default=[]),
    session_id: Optional[str] = Cookie(default=None)
):
    if not query.strip():
        return templates.TemplateResponse(
            "partials/results.html",
            {"request": request, "results": [], "query": ""}
        )

    qdrant = request.app.state.qdrant_client
    embeddings = request.app.state.embedding_service
    sessions = request.app.state.session_store
    settings = get_settings()

    # Use all collections if none selected
    if not collections:
        collections = settings.collections

    # Generate embedding and search
    query_vector = embeddings.embed(query)
    results = qdrant.search(
        query_vector=query_vector,
        collections=collections,
        limit=settings.default_limit,
        score_threshold=settings.default_score_threshold
    )

    # Track in session
    if session_id:
        sessions.add_query(
            session_id=session_id,
            query=query,
            result_count=len(results),
            collections=collections
        )

    return templates.TemplateResponse(
        "partials/results.html",
        {
            "request": request,
            "results": results,
            "query": query
        }
    )


@app.get("/partials/history", response_class=HTMLResponse)
async def history_partial(
    request: Request,
    session_id: Optional[str] = Cookie(default=None)
):
    sessions = request.app.state.session_store
    history = []

    if session_id:
        history = sessions.get_history(session_id)

    return templates.TemplateResponse(
        "partials/history.html",
        {"request": request, "history": list(reversed(history))}
    )


@app.get("/partials/sources/{collection}", response_class=HTMLResponse)
async def sources_partial(request: Request, collection: str):
    qdrant = request.app.state.qdrant_client
    sources = qdrant.get_unique_sources(collection)

    return templates.TemplateResponse(
        "partials/sources.html",
        {"request": request, "collection": collection, "sources": sources}
    )


@app.get("/partials/document/{collection}", response_class=HTMLResponse)
async def document_partial(request: Request, collection: str, source: str):
    qdrant = request.app.state.qdrant_client
    docs = qdrant.get_documents_by_source(collection, source)

    return templates.TemplateResponse(
        "partials/document.html",
        {"request": request, "source": source, "documents": docs}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
