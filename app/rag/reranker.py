from app.config import settings


class NoOpReranker:
    def rerank(self, question: str, documents: list):
        return documents[: settings.RERANK_TOP_K]


class CrossEncoderReranker:
    def __init__(self, model_name: str):
        from sentence_transformers import CrossEncoder

        self.model = CrossEncoder(model_name)

    def rerank(self, question: str, documents: list):
        if not documents:
            return []

        pairs = [(question, doc.page_content) for doc in documents]
        scores = self.model.predict(pairs)

        ranked_documents = sorted(
            zip(documents, scores),
            key=lambda item: item[1],
            reverse=True,
        )

        return [
            document
            for document, _ in ranked_documents[: settings.RERANK_TOP_K]
        ]