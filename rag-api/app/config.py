from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Qdrant
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333

    # Embedding model
    embedding_model: str = "all-MiniLM-L6-v2"

    # Collections
    collections: list[str] = ["external_docs", "rugs_protocol", "rl_design"]

    # Search defaults
    default_limit: int = 10
    default_score_threshold: float = 0.3

    # Session settings
    max_sessions: int = 1000
    max_history_per_session: int = 100
    session_ttl_hours: int = 24

    # App settings
    app_title: str = "RAG Knowledge API"
    debug: bool = False

    class Config:
        env_prefix = ""
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    return Settings()
