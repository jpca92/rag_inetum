from app.config import settings
from app.rag.embeddings import HuggingFaceEmbeddingModel
from app.rag.llm import HuggingFaceLocalLLM


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


class LLMFactory:
    @staticmethod
    def create():
        if settings.LLM_PROVIDER == "hf_local":
            return HuggingFaceLocalLLM(
                model_name=settings.LLM_MODEL,
            )

        raise ValueError(
            f"Unsupported LLM provider: {settings.LLM_PROVIDER}"
        )