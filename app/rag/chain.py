from functools import lru_cache

from app.conversation.repository import ConversationRepository
from app.patterns.factories import EmbeddingFactory, LLMFactory
from app.patterns.facade import RAGFacade
from app.rag.retriever import RAGRetriever
from app.rag.vector_store import ChromaVectorStore


@lru_cache
def get_rag_facade() -> RAGFacade:
    embeddings = EmbeddingFactory.create()
    vector_store = ChromaVectorStore(embeddings)
    retriever = RAGRetriever(vector_store.as_retriever())
    llm = LLMFactory.create()
    repository = ConversationRepository()

    return RAGFacade(
        retriever=retriever,
        llm_client=llm,
        repository=repository,
    )