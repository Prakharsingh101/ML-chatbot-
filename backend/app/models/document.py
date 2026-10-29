"""SQLAlchemy models for documents and vector chunks."""
import uuid
from datetime import datetime, timezone
from typing import Optional
# pyrefly: ignore [missing-import]
from sqlalchemy import String, Text, Integer, BigInteger, DateTime, ForeignKey, Uuid
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

try:
    # pyrefly: ignore [missing-import]
    from pgvector.sqlalchemy import Vector
    PGVECTOR_AVAILABLE = True
except ImportError:
    PGVECTOR_AVAILABLE = False
    Vector = None


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Document(Base):
    """Document metadata entity."""

    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    content_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    file_size: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )
    file_hash: Mapped[Optional[str]] = mapped_column(
        String(64),
        nullable=True,
        index=True,
    )
    version: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        default="uploaded",
        nullable=False,
    )  # uploaded, processing, indexed, failed
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
    )

    chunks: Mapped[list["DocumentChunk"]] = relationship(
        "DocumentChunk",
        back_populates="document",
        cascade="all, delete-orphan",
        order_by="DocumentChunk.chunk_index.asc()",
    )


class DocumentChunk(Base):
    """Document text chunks with vector embeddings."""

    __tablename__ = "document_chunks"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    document_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    chunk_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    embedding = mapped_column(
        Vector(768) if Vector is not None else Text,
        nullable=True,
    )
    page_number: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    document: Mapped["Document"] = relationship(
        "Document",
        back_populates="chunks",
    )
