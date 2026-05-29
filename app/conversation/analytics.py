import json
import sqlite3
from collections import Counter

from app.config import settings


class ConversationAnalytics:
    def __init__(self, db_path: str = settings.SQLITE_DB_PATH):
        self.db_path = db_path

    def summary(self) -> dict:
        with sqlite3.connect(self.db_path) as conn:
            total_sessions = conn.execute(
                """
                SELECT COUNT(DISTINCT session_id)
                FROM messages
                """
            ).fetchone()[0]

            total_messages = conn.execute(
                """
                SELECT COUNT(*)
                FROM messages
                """
            ).fetchone()[0]

            total_questions = conn.execute(
                """
                SELECT COUNT(*)
                FROM messages
                WHERE role = 'user'
                """
            ).fetchone()[0]

            average_latency = conn.execute(
                """
                SELECT AVG(latency_ms)
                FROM rag_events
                """
            ).fetchone()[0]

        return {
            "total_sessions": total_sessions or 0,
            "total_messages": total_messages or 0,
            "total_questions": total_questions or 0,
            "average_latency_ms": round(average_latency or 0, 2),
        }

    def top_questions(self, limit: int = 10) -> list[dict]:
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                """
                SELECT content
                FROM messages
                WHERE role = 'user'
                """
            ).fetchall()

        counter = Counter(row[0].strip().lower() for row in rows)

        return [
            {
                "question": question,
                "count": count,
            }
            for question, count in counter.most_common(limit)
        ]

    def top_sources(self, limit: int = 10) -> list[dict]:
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                """
                SELECT retrieved_sources
                FROM rag_events
                """
            ).fetchall()

        urls = []

        for (source_json,) in rows:
            try:
                sources = json.loads(source_json or "[]")

                for source in sources:
                    url = source.get("url")

                    if url:
                        urls.append(url)

            except json.JSONDecodeError:
                continue

        counter = Counter(urls)

        return [
            {
                "url": url,
                "count": count,
            }
            for url, count in counter.most_common(limit)
        ]