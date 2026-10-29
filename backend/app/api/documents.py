"""Documents API router for uploading, listing, and retrieving RAG documents."""
import hashlib
import logging
from uuid import UUID
from pathlib import Path

# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
# pyrefly: ignore [missing-import]
from sqlalchemy import select, func
# pyrefly: ignore [missing-import]
from sqlalchemy.ext.asyncio import AsyncSession
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.database import get_db
from app.core.security import resolve_safe_upload_path
from app.models.document import Document, DocumentChunk
from app.schemas.document import DocumentResponse, DocumentChunkResponse
from app.services.rag_service import rag_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
) -> DocumentResponse:
    """Upload a document (PDF, TXT, MD, DOCX), persist it, and generate vector index."""
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file must have a filename.",
        )

    # 1. Validate file size and resolve safe destination path
    content = await file.read()
    file_size = len(content)

    if file_size > settings.max_upload_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE_MB}MB.",
        )

    safe_target_path = resolve_safe_upload_path(file.filename)
    safe_target_path.write_bytes(content)

    file_hash = hashlib.sha256(content).hexdigest()

    # 2. Create document record
    doc = Document(
        filename=safe_target_path.name,
        content_type=file.content_type or "application/octet-stream",
        file_size=file_size,
        file_hash=file_hash,
        status="uploaded",
    )
    db.add(doc)
    await db.flush()

    # 3. Index document via RAG service
    chunk_count = await rag_service.index_document(db, doc, safe_target_path)

    return DocumentResponse(
        id=doc.id,
        filename=doc.filename,
        content_type=doc.content_type,
        file_size=doc.file_size,
        version=doc.version,
        status=doc.status,
        created_at=doc.created_at,
        updated_at=doc.updated_at,
        chunk_count=chunk_count,
    )


@router.get("", response_model=list[DocumentResponse], summary="List all indexed documents")
async def list_documents(
    db: AsyncSession = Depends(get_db),
) -> list[DocumentResponse]:
    """Retrieve all uploaded companion documents with chunk counts."""
    stmt = (
        select(Document, func.count(DocumentChunk.id).label("chunk_count"))
        .outerjoin(DocumentChunk, Document.id == DocumentChunk.document_id)
        .group_by(Document.id)
        .order_by(Document.created_at.desc())
    )
    result = await db.execute(stmt)
    rows = result.all()

    items = []
    for doc, chunk_count in rows:
        items.append(
            DocumentResponse(
                id=doc.id,
                filename=doc.filename,
                content_type=doc.content_type,
                file_size=doc.file_size,
                version=doc.version,
                status=doc.status,
                created_at=doc.created_at,
                updated_at=doc.updated_at,
                chunk_count=chunk_count,
            )
        )
    return items


@router.get("/{document_id}", response_model=DocumentResponse, summary="Get document details")
async def get_document(
    document_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> DocumentResponse:
    """Retrieve single document details."""
    stmt = (
        select(Document, func.count(DocumentChunk.id).label("chunk_count"))
        .outerjoin(DocumentChunk, Document.id == DocumentChunk.document_id)
        .where(Document.id == document_id)
        .group_by(Document.id)
    )
    result = await db.execute(stmt)
    row = result.first()
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID '{document_id}' was not found.",
        )
    doc, chunk_count = row
    return DocumentResponse(
        id=doc.id,
        filename=doc.filename,
        content_type=doc.content_type,
        file_size=doc.file_size,
        version=doc.version,
        status=doc.status,
        created_at=doc.created_at,
        updated_at=doc.updated_at,
        chunk_count=chunk_count,
    )


@router.get("/{document_id}/chunks", response_model=list[DocumentChunkResponse], summary="Get chunks for a document")
async def get_document_chunks(
    document_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> list[DocumentChunkResponse]:
    """Retrieve all chunks belonging to a document."""
    stmt = (
        select(DocumentChunk)
        .where(DocumentChunk.document_id == document_id)
        .order_by(DocumentChunk.chunk_index.asc())
    )
    result = await db.execute(stmt)
    chunks = result.scalars().all()
    return [
        DocumentChunkResponse(
            id=c.id,
            document_id=c.document_id,
            chunk_index=c.chunk_index,
            content=c.content,
            page_number=c.page_number,
        )
        for c in chunks
    ]


@router.delete("/{document_id}", status_code=status.HTTP_200_OK, summary="Delete a document")
async def delete_document(
    document_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Delete document, cascading its chunks, and removing the file on disk."""
    stmt = select(Document).where(Document.id == document_id)
    result = await db.execute(stmt)
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID '{document_id}' was not found.",
        )

    # Remove physical file if present
    file_path = settings.upload_path / doc.filename
    if file_path.exists():
        try:
            file_path.unlink()
        except Exception as exc:
            logger.warning(f"Failed to delete file on disk: {exc}")

    await db.delete(doc)
    await db.commit()
    return {"status": "success", "message": f"Document '{doc.filename}' deleted successfully."}

