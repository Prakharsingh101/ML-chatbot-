"""Pydantic schemas for document metadata and chunk management."""
from datetime import datetime
from typing import Optional
from uuid import UUID
# pyrefly: ignore [missing-import]
from pydantic import BaseModel


class DocumentResponse(BaseModel):
    """Metadata response for an uploaded document."""

    id: UUID
    filename: str
    content_type: str
    file_size: int
    version: int
    status: str
    created_at: datetime
    updated_at: datetime
    chunk_count: int = 0

    model_config = {"from_attributes": True}


class DocumentChunkResponse(BaseModel):
    """Retrieved document chunk for RAG context and citations."""

    id: UUID
    document_id: UUID
    chunk_index: int
    content: str
    page_number: Optional[int] = None
    similarity_score: Optional[float] = None

    model_config = {"from_attributes": True}
