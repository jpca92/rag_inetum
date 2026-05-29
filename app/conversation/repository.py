import sqlite3
from pathlib import Path

from app.config import settings


class ConversationRepository:
    def __init__(self, db_path: str = settings.SQLITE_DB_PATH):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS rag_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    retrieved_sources TEXT,
                    latency_ms INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

    def save_message(self, session_id: str, role: str, content: str) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO messages (session_id, role, content)
                VALUES (?, ?, ?)
                """,
                (session_id, role, content),
            )

    def get_last_messages(self, session_id: str, limit: int) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT role, content, created_at
                FROM messages
                WHERE session_id = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (session_id, limit),
            ).fetchall()

        messages = [
            {
                "role": role,
                "content": content,
                "created_at": created_at,
            }
            for role, content, created_at in rows
        ]

        return list(reversed(messages))

    def save_rag_event(
        self,
        session_id: str,
        question: str,
        answer: str,
        retrieved_sources: str,
        latency_ms: int,
    ) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO rag_events (
                    session_id,
                    question,
                    answer,
                    retrieved_sources,
                    latency_ms
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    session_id,
                    question,
                    answer,
                    retrieved_sources,
                    latency_ms,
                ),
            )

    def list_sessions(self) -> list[str]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT DISTINCT session_id
                FROM messages
                ORDER BY session_id
                """
            ).fetchall()

        return [row[0] for row in rows]

    def get_session_messages(self, session_id: str) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT role, content, created_at
                FROM messages
                WHERE session_id = ?
                ORDER BY id ASC
                """,
                (session_id,),
            ).fetchall()

        return [
            {
                "role": role,
                "content": content,
                "created_at": created_at,
            }
            for role, content, created_at in rows
        ]