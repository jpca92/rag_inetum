from typing import Any

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    session_id: str = Field(..., examples=["test-user-001"])
    question: str = Field(..., examples=["¿Qué tipo de cuentas ofrece el banco?"])


class ChatResponse(BaseModel):
    session_id: str
    answer: str
    sources: list[dict[str, Any]]


class ScrapeResponse(BaseModel):
    pages_scraped: int
    raw_path: str
    clean_path: str


class IngestResponse(BaseModel):
    chunks_indexed: int
    vector_db_path: str