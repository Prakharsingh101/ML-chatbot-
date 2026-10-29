"""Pydantic schemas for conversation management."""
from datetime import datetime
from uuid import UUID
# pyrefly: ignore [missing-import]
from pydantic import BaseModel
from app.schemas.chat import MessageResponse


class ConversationListItem(BaseModel):
    """Summary item for conversation listings in the sidebar."""

    id: UUID
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: int = 0

    model_config = {"from_attributes": True}


class ConversationDetailResponse(BaseModel):
    """Detailed conversation view with full message history."""

    id: UUID
    title: str
    created_at: datetime
    updated_at: datetime
    messages: list[MessageResponse] = []

    model_config = {"from_attributes": True}
