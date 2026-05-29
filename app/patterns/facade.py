import json
import time

from app.conversation.memory import ConversationMemory
from app.conversation.repository import ConversationRepository
from app.rag.retriever import RAGRetriever


class RAGFacade:
    def __init__(
        self,
        retriever: RAGRetriever,
        llm_client,
        repository: ConversationRepository,
    ):
        self.retriever = retriever
        self.llm_client = llm_client
        self.repository = repository
        self.memory = ConversationMemory(repository)

    def ask(self, session_id: str, question: str) -> dict:
        start = time.perf_counter()

        history = self.memory.get_formatted_history(session_id)
        documents = self.retriever.retrieve(question)
        context = self._format_context(documents)

        answer = self.llm_client.generate_answer(
            question=question,
            context=context,
            history=history,
        )

        sources = self._format_sources(documents)
        latency_ms = int((time.perf_counter() - start) * 1000)

        self.repository.save_message(
            session_id=session_id,
            role="user",
            content=question,
        )

        self.repository.save_message(
            session_id=session_id,
            role="assistant",
            content=answer,
        )

        self.repository.save_rag_event(
            session_id=session_id,
            question=question,
            answer=answer,
            retrieved_sources=json.dumps(sources, ensure_ascii=False),
            latency_ms=latency_ms,
        )

        return {
            "session_id": session_id,
            "answer": answer,
            "sources": sources,
        }

    def _format_context(self, documents: list) -> str:
        blocks = []

        for index, document in enumerate(documents, start=1):
            title = document.metadata.get("title", "Sin título")
            url = document.metadata.get("url", "")

            blocks.append(
                f"""
[Fuente {index}]
Título: {title}
URL: {url}
Contenido: {document.page_content}
""".strip()
            )

        return "\n\n".join(blocks)

    def _format_sources(self, documents: list) -> list[dict]:
        return [
            {
                "title": document.metadata.get("title", "Sin título"),
                "url": document.metadata.get("url", ""),
                "preview": document.page_content[:220],
            }
            for document in documents
        ]