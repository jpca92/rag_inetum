from fastapi import FastAPI, HTTPException

from app.config import settings
from app.conversation.repository import ConversationRepository
from app.patterns.factories import EmbeddingFactory
from app.rag.chain import get_rag_facade
from app.rag.vector_store import ChromaVectorStore
from app.schemas import ChatRequest, ChatResponse, IngestResponse, ScrapeResponse
from app.scraping.scraper import WebsiteScraper


app = FastAPI(
    title="RAG Banking Assistant",
    description="Sistema RAG local con web scraping, historial conversacional y analítica.",
    version="0.1.0",
)


@app.get("/health")
def health():
    return {
        "status": "ok",
    }


@app.post("/scrape", response_model=ScrapeResponse)
def scrape():
    scraper = WebsiteScraper()
    raw_pages, clean_documents = scraper.scrape()

    return ScrapeResponse(
        pages_scraped=len(clean_documents),
        raw_path=settings.RAW_DATA_PATH,
        clean_path=settings.CLEAN_DATA_PATH,
    )


@app.post("/ingest", response_model=IngestResponse)
def ingest():
    embeddings = EmbeddingFactory.create()
    vector_store = ChromaVectorStore(embeddings)
    chunks_indexed = vector_store.ingest_from_clean_file()

    if chunks_indexed == 0:
        raise HTTPException(
            status_code=400,
            detail="No hay documentos limpios para indexar. Ejecuta /scrape primero.",
        )

    return IngestResponse(
        chunks_indexed=chunks_indexed,
        vector_db_path=settings.VECTOR_DB_PATH,
    )


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    rag = get_rag_facade()

    return rag.ask(
        session_id=request.session_id,
        question=request.question,
    )


@app.get("/sessions")
def sessions():
    repository = ConversationRepository()

    return {
        "sessions": repository.list_sessions(),
    }


@app.get("/sessions/{session_id}/messages")
def session_messages(session_id: str):
    repository = ConversationRepository()

    return {
        "session_id": session_id,
        "messages": repository.get_session_messages(session_id),
    }