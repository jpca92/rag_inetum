from app.config import settings
from app.rag.embeddings import HuggingFaceEmbeddingModel


class EmbeddingFactory:
    @staticmethod
    def create():
        if settings.EMBEDDING_PROVIDER == "huggingface":
            return HuggingFaceEmbeddingModel(
                settings.EMBEDDING_MODEL
            ).create()

        raise ValueError(
            f"Unsupported embedding provider: {settings.EMBEDDING_PROVIDER}"
        )