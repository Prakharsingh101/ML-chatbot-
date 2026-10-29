"""Pydantic schemas for chat endpoints."""
from datetime import datetime
from typing import Optional, Any
from uuid import UUID
# pyrefly: ignore [missing-import]
from pydantic import BaseModel, Field, field_validator


class ChatMessageRequest(BaseModel):
    """Request payload for sending a chat message."""

    message: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="The user prompt or question.",
    )
    conversation_id: Optional[UUID] = Field(
        default=None,
        description="Optional existing conversation ID to continue.",
    )
    use_rag: bool = Field(
        default=True,
        description="Whether to retrieve relevant passages from uploaded documents.",
    )
    use_web_search: bool = Field(
        default=False,
        description="Whether to query live web search to ground real-time information.",
    )
    image_data: Optional[str] = Field(
        default=None,
        description="Optional base64-encoded image string for multimodal scene analysis.",
    )

    @field_validator("message")
    @classmethod
    def validate_message_not_empty(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Message cannot be empty or pure whitespace.")
        return stripped


class MessageResponse(BaseModel):
    """Chat message response structure."""

    id: UUID
    conversation_id: UUID
    role: str
    content: str
    metadata: Optional[dict[str, Any]] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatResponse(BaseModel):
    """Response returned after processing a chat interaction."""

    conversation_id: UUID
    conversation_title: str
    message: MessageResponse
