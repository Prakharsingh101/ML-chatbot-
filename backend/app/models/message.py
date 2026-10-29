"""SQLAlchemy model for chat messages."""
import uuid
from datetime import datetime, timezone
from typing import Optional, Any
# pyrefly: ignore [missing-import]
from sqlalchemy import String, Text, DateTime, ForeignKey, JSON, Uuid
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Message(Base):
    """Message entity representing user or assistant chat turns."""

    __tablename__ = "messages"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    conversation_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )  # 'user', 'assistant', 'system'
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    msg_metadata: Mapped[Optional[dict[str, Any]]] = mapped_column(
        "metadata",
        JSON,
        nullable=True,
        default=dict,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
        index=True,
    )

    # Back reference to conversation
    Conversation = None
    conversation: Mapped["Conversation"] = relationship(
        "Conversation",
        back_populates="messages",
    )
