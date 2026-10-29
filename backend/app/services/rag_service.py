"""RAG (Retrieval-Augmented Generation) pipeline and document chunking service."""
import logging
import math
from pathlib import Path
from typing import Optional
from uuid import UUID

# pyrefly: ignore [missing-import]
from sqlalchemy import select
# pyrefly: ignore [missing-import]
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document, DocumentChunk, PGVECTOR_AVAILABLE
from app.services.ai_service import ai_service

logger = logging.getLogger(__name__)


def extract_text_from_file(file_path: Path, content_type: str = "") -> str:
    """Extract plain text from PDF, DOCX, TXT, or Markdown documents."""
    suffix = file_path.suffix.lower()

    # 1. Plain text / Markdown
    if suffix in [".txt", ".md", ".markdown", ".csv", ".json", ".log"] or "text" in content_type:
        try:
            return file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return file_path.read_text(encoding="latin-1", errors="replace")

    # 2. PDF documents via PyMuPDF (fitz)
    if suffix == ".pdf" or "pdf" in content_type:
        try:
            # pyrefly: ignore [missing-import]
            import fitz
            doc = fitz.open(str(file_path))
            pages = []
            for page in doc:
                text = page.get_text()
                if text:
                    pages.append(text)
            doc.close()
            return "\n\n".join(pages)
        except Exception as exc:
            logger.warning(f"PyMuPDF failed or not available for PDF extraction: {exc}")

    # 3. Word documents (.docx) via python-docx
    if suffix == ".docx" or "wordprocessing" in content_type:
        try:
            # pyrefly: ignore [missing-import]
            import docx
            doc = docx.Document(str(file_path))
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            return "\n\n".join(paragraphs)
        except Exception as exc:
            logger.warning(f"python-docx failed or not available for DOCX extraction: {exc}")

    # Fallback raw byte decoding
    try:
        raw_bytes = file_path.read_bytes()
        return raw_bytes.decode("utf-8", errors="ignore")
    except Exception as exc:
        logger.error(f"Failed to read file '{file_path}': {exc}")
        return ""


def chunk_text(
    text: str,
    chunk_size: int = 500,
    overlap: int = 50,
) -> list[str]:
    """Split long text into overlapping chunks for semantic embedding."""
    cleaned = text.strip()
    if not cleaned:
        return []

    if len(cleaned) <= chunk_size:
        return [cleaned]

    chunks = []
    start = 0
    while start < len(cleaned):
        end = start + chunk_size
        chunk = cleaned[start:end]

        if end < len(cleaned):
            last_period = max(chunk.rfind(". "), chunk.rfind(".\n"), chunk.rfind("\n"))
            if last_period > chunk_size // 2:
                chunk = chunk[: last_period + 1]
                end = start + len(chunk)

        chunks.append(chunk.strip())
        start = end - overlap
        if start >= len(cleaned):
            break

    return [c for c in chunks if c]


class RAGService:
    """Orchestrates document indexing, chunk embeddings, and semantic vector retrieval."""

    async def index_document(
        self,
        db: AsyncSession,
        document: Document,
        file_path: Path,
    ) -> int:
        """Extract text, chunk, generate embeddings, and persist DocumentChunk records."""
        try:
            document.status = "processing"
            await db.commit()

            raw_text = extract_text_from_file(file_path, document.content_type)
            if not raw_text.strip():
                document.status = "empty"
                await db.commit()
                return 0

            chunks = chunk_text(raw_text, chunk_size=600, overlap=60)
            chunk_records = []

            for idx, chunk_content in enumerate(chunks):
                # Generate embedding via Gemini text-embedding-004
                embedding_vector = await ai_service.generate_embedding(chunk_content)

                chunk_records.append(
                    DocumentChunk(
                        document_id=document.id,
                        chunk_index=idx,
                        content=chunk_content,
                        embedding=embedding_vector if PGVECTOR_AVAILABLE else None,
                        page_number=None,
                    )
                )

            db.add_all(chunk_records)
            document.status = "indexed"
            await db.commit()
            logger.info(f"Indexed document '{document.filename}' with {len(chunk_records)} chunks.")
            return len(chunk_records)

        except Exception as exc:
            logger.error(f"Failed to index document '{document.filename}': {exc}")
            document.status = "failed"
            await db.commit()
            return 0

    async def search_relevant_chunks(
        self,
        db: AsyncSession,
        query: str,
        top_k: int = 3,
        document_id: Optional[UUID] = None,
    ) -> list[DocumentChunk]:
        """
        Search for top_k relevant text chunks matching the user's query.
        Uses pgvector cosine distance if available, or keyword matching fallback.
        """
        if not query.strip():
            return []

        try:
            query_embedding = await ai_service.generate_embedding(query)

            # Check if pgvector is active in models and vector is not pure zeroes
            if PGVECTOR_AVAILABLE and any(v != 0.0 for v in query_embedding):
                stmt = select(DocumentChunk)
                if document_id:
                    stmt = stmt.where(DocumentChunk.document_id == document_id)
                stmt = stmt.order_by(DocumentChunk.embedding.cosine_distance(query_embedding)).limit(top_k)
                result = await db.execute(stmt)
                return list(result.scalars().all())

            # Fallback: Query recent chunks with keyword matching
            stmt = select(DocumentChunk)
            if document_id:
                stmt = stmt.where(DocumentChunk.document_id == document_id)
            stmt = stmt.order_by(DocumentChunk.created_at.desc()).limit(20)
            result = await db.execute(stmt)
            all_chunks = list(result.scalars().all())

            # Keyword match scoring
            query_words = set(query.lower().split())
            scored = []
            for c in all_chunks:
                text_lower = c.content.lower()
                matches = sum(1 for w in query_words if w in text_lower)
                scored.append((matches, c))
            scored.sort(key=lambda x: x[0], reverse=True)
            return [c for score, c in scored[:top_k] if score > 0] or all_chunks[:top_k]

        except Exception as exc:
            logger.warning(f"Error during semantic vector search: {exc}")
            return []

    def format_rag_context(self, chunks: list[DocumentChunk]) -> str:
        """Format retrieved chunks into a cohesive context prompt string for Gemini."""
        if not chunks:
            return ""
        formatted_snippets = []
        for i, c in enumerate(chunks, 1):
            snippet = f"[Passage {i}]:\n{c.content.strip()}"
            formatted_snippets.append(snippet)
        return "\n\n".join(formatted_snippets)


rag_service = RAGService()
