import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.patterns.factories import EmbeddingFactory
from app.rag.vector_store import ChromaVectorStore


if __name__ == "__main__":
    embeddings = EmbeddingFactory.create()
    vector_store = ChromaVectorStore(embeddings)

    chunks = vector_store.ingest_from_clean_file()

    print(f"Chunks indexed: {chunks}")
