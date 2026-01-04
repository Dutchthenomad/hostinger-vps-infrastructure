from datetime import datetime
from uuid import uuid4
from collections import OrderedDict
from dataclasses import dataclass, field

from app.config import get_settings


@dataclass
class QueryRecord:
    id: int
    query: str
    timestamp: datetime
    result_count: int
    collections: list[str]


@dataclass
class Session:
    session_id: str
    created_at: datetime
    queries: list[QueryRecord] = field(default_factory=list)


class SessionStore:
    def __init__(self):
        settings = get_settings()
        self.sessions: OrderedDict[str, Session] = OrderedDict()
        self.max_sessions = settings.max_sessions
        self.max_history = settings.max_history_per_session

    def create_session(self) -> str:
        session_id = str(uuid4())
        self.sessions[session_id] = Session(
            session_id=session_id,
            created_at=datetime.utcnow()
        )
        self._cleanup_old_sessions()
        return session_id

    def get_session(self, session_id: str) -> Session | None:
        return self.sessions.get(session_id)

    def get_or_create_session(self, session_id: str | None) -> str:
        if session_id and session_id in self.sessions:
            return session_id
        return self.create_session()

    def add_query(
        self,
        session_id: str,
        query: str,
        result_count: int,
        collections: list[str]
    ) -> None:
        session = self.sessions.get(session_id)
        if not session:
            return

        query_record = QueryRecord(
            id=len(session.queries) + 1,
            query=query,
            timestamp=datetime.utcnow(),
            result_count=result_count,
            collections=collections
        )
        session.queries.append(query_record)

        if len(session.queries) > self.max_history:
            session.queries = session.queries[-self.max_history:]

    def get_history(self, session_id: str) -> list[QueryRecord]:
        session = self.sessions.get(session_id)
        if not session:
            return []
        return session.queries

    def delete_session(self, session_id: str) -> bool:
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False

    def _cleanup_old_sessions(self) -> None:
        while len(self.sessions) > self.max_sessions:
            self.sessions.popitem(last=False)
