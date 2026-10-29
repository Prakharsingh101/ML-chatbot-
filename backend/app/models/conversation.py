"""SQLAlchemy model for conversations."""
import uuid
from datetime import datetime, timezone
# pyrefly: ignore [missing-import]
from sqlalchemy import String, DateTime, Uuid
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Conversation(Base):
    """Conversation entity holding chat sessions."""

    __tablename__ = "conversations"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        default="New Conversation",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
        index=True,
    )

    # Relationship to messages with cascade deletion
    messages: Mapped[list["Message"]] = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="Message.created_at.asc()",
    )
