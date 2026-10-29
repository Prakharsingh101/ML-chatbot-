"""Chat API endpoint handling multi-turn conversation and AI generation."""
import logging
from uuid import UUID
# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, HTTPException, status
# pyrefly: ignore [missing-import]
from sqlalchemy import select
# pyrefly: ignore [missing-import]
from sqlalchemy.ext.asyncio import AsyncSession
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.database import get_db
from app.models.conversation import Conversation
from app.models.message import Message
from app.schemas.chat import ChatMessageRequest, ChatResponse, MessageResponse
from app.services.ai_service import ai_service
from app.services.rag_service import rag_service
from app.services.search_service import search_service

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Chat"])


@router.post("/chat", response_model=ChatResponse, summary="Send message and receive AI response")
async def send_chat_message(
    payload: ChatMessageRequest,
    db: AsyncSession = Depends(get_db),
) -> ChatResponse:
    """
    Process a user message, persist turns in the database, and generate an AI response.
    Creates a new conversation if `conversation_id` is not supplied.
    """
    conversation: Conversation
    history_turns: list[dict[str, str]] = []

    # 1. Retrieve or create conversation
    if payload.conversation_id:
        result = await db.execute(
            select(Conversation)
            .options(selectinload(Conversation.messages))
            .where(Conversation.id == payload.conversation_id)
        )
        existing = result.scalar_one_or_none()
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation with ID '{payload.conversation_id}' was not found.",
            )
        conversation = existing
        # Extract prior turns for multi-turn conversational context
        for m in (conversation.messages or [])[-10:]:
            history_turns.append({"role": m.role, "content": m.content})
    else:
        # Generate initial title from prompt
        title = ai_service.generate_title(payload.message)
        conversation = Conversation(title=title)
        db.add(conversation)
        await db.flush()  # Populates conversation.id

    # 2. Store user message
    user_msg = Message(
        conversation_id=conversation.id,
        role="user",
        content=payload.message,
        msg_metadata={},
    )
    db.add(user_msg)
    await db.flush()

    # 3. Retrieve Grounded Context (RAG & Web Search)
    context_sections = []

    if payload.use_rag:
        try:
            chunks = await rag_service.search_relevant_chunks(db, query=payload.message, top_k=3)
            if chunks:
                rag_snippet = rag_service.format_rag_context(chunks)
                if rag_snippet:
                    context_sections.append(f"Relevant Knowledge Base Information:\n{rag_snippet}")
        except Exception as rag_err:
            logger.warning(f"RAG context retrieval failed: {rag_err}")

    if payload.use_web_search:
        try:
            search_results = await search_service.search(query=payload.message, max_results=3)
            if search_results:
                search_snippet = search_service.format_search_context(search_results)
                if search_snippet:
                    context_sections.append(f"Live Web Search Information:\n{search_snippet}")
        except Exception as search_err:
            logger.warning(f"Web search retrieval failed: {search_err}")

    grounded_context = "\n\n---\n\n".join(context_sections) if context_sections else None

    # 4. Generate AI response
    try:
        ai_content = await ai_service.generate_response(
            prompt=payload.message,
            conversation_history=history_turns,
            context=grounded_context,
            image_data=payload.image_data,
        )
    except Exception as exc:
        logger.error(f"Error during AI generation: {exc}")
        ai_content = (
            "I'm sorry, I encountered a temporary connection issue while thinking. "
            "Please feel free to try sending your message again."
        )

    # 4. Store assistant message
    assistant_msg = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=ai_content,
        msg_metadata={"model": settings.GEMINI_MODEL},
    )
    db.add(assistant_msg)

    # 5. Commit transaction and refresh
    await db.commit()
    await db.refresh(assistant_msg)
    await db.refresh(conversation)

    return ChatResponse(
        conversation_id=conversation.id,
        conversation_title=conversation.title,
        message=MessageResponse(
            id=assistant_msg.id,
            conversation_id=assistant_msg.conversation_id,
            role=assistant_msg.role,
            content=assistant_msg.content,
            metadata=assistant_msg.msg_metadata,
            created_at=assistant_msg.created_at,
        ),
    )
