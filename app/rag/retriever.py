from app.config import settings
from app.rag.reranker import CrossEncoderReranker, NoOpReranker


class RAGRetriever:
    def __init__(self, retriever):
        self.retriever = retriever

        if settings.ENABLE_RERANKER:
            self.reranker = CrossEncoderReranker(settings.RERANKER_MODEL)
        else:
            self.reranker = NoOpReranker()

    def retrieve(self, question: str):
        documents = self.retriever.invoke(question)
        return self.reranker.rerank(question, documents)