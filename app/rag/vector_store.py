from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import settings
from app.scraping.storage import read_jsonl


class ChromaVectorStore:
    def __init__(self, embeddings):
        self.embeddings = embeddings
        self.persist_directory = settings.VECTOR_DB_PATH

    def ingest_from_clean_file(self) -> int:
        rows = read_jsonl(settings.CLEAN_DATA_PATH)

        documents = [
            Document(
                page_content=row["content"],
                metadata={
                    "url": row.get("url", ""),
                    "title": row.get("title", ""),
                },
            )
            for row in rows
        ]

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
        )

        chunks = splitter.split_documents(documents)

        if not chunks:
            return 0

        Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            persist_directory=self.persist_directory,
            collection_name="banking_docs",
        )

        return len(chunks)

    def as_retriever(self):
        vector_store = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings,
            collection_name="banking_docs",
        )

        return vector_store.as_retriever(
            search_kwargs={"k": settings.TOP_K}
        )