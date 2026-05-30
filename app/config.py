from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_ENV: str = "local"

    SCRAPER_START_URL: str = "https://www.bbva.com.co/"
    SCRAPER_ALLOWED_DOMAIN: str = "www.bbva.com.co"
    SCRAPER_MAX_PAGES: int = 25
    SCRAPER_TIMEOUT_SECONDS: int = 15

    RAW_DATA_PATH: str = "/app/data/raw/pages.jsonl"
    CLEAN_DATA_PATH: str = "/app/data/clean/documents.jsonl"
    VECTOR_DB_PATH: str = "/app/data/chroma"
    SQLITE_DB_PATH: str = "/app/database/conversations.db"

    EMBEDDING_PROVIDER: str = "huggingface"
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"

    LLM_PROVIDER: str = "hf_local"
    LLM_MODEL: str = "LiquidAI/LFM2.5-350M"
    MAX_NEW_TOKENS: int = 384
    TEMPERATURE: float = 0.1

    CHUNK_SIZE: int = 800
    CHUNK_OVERLAP: int = 120
    TOP_K: int = 8
    RERANK_TOP_K: int = 4
    MEMORY_N_MESSAGES: int = 6

    ENABLE_RERANKER: bool = False
    RERANKER_MODEL: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()