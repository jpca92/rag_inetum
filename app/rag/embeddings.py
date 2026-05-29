from langchain_community.embeddings import HuggingFaceEmbeddings


class HuggingFaceEmbeddingModel:
    def __init__(self, model_name: str):
        self.model_name = model_name

    def create(self):
        return HuggingFaceEmbeddings(
            model_name=self.model_name,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )