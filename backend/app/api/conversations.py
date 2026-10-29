"""Conversations API router for history and session management."""
import logging
from uuid import UUID
# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, HTTPException, status
# pyrefly: ignore [missing-import]
from sqlalchemy import select, func
# pyrefly: ignore [missing-import]
from sqlalchemy.ext.asyncio import AsyncSession
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.conversation import Conversation
from app.models.message import Message
from app.schemas.conversation import ConversationListItem, ConversationDetailResponse
from app.schemas.chat import MessageResponse

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Conversations"])


@router.get(
    "/conversations",
    response_model=list[ConversationListItem],
    summary="List all conversations",
)
async def list_conversations(
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
) -> list[ConversationListItem]:
    """
    Retrieve all conversation sessions ordered by most recently active.
    Includes total message count for each conversation.
    """
    # Query conversations with message count via left join
    stmt = (
        select(
            Conversation,
            func.count(Message.id).label("message_count"),
        )
        .outerjoin(Message, Conversation.id == Message.conversation_id)
        .group_by(Conversation.id)
        .order_by(Conversation.updated_at.desc())
        .offset(offset)
        .limit(min(limit, 100))
    )
    result = await db.execute(stmt)
    rows = result.all()

    items = []
    for conv, msg_count in rows:
        items.append(
            ConversationListItem(
                id=conv.id,
                title=conv.title,
                created_at=conv.created_at,
                updated_at=conv.updated_at,
                message_count=msg_count,
            )
        )
    return items


@router.get(
    "/conversations/{conversation_id}",
    response_model=ConversationDetailResponse,
    summary="Get conversation details and messages",
)
async def get_conversation(
    conversation_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> ConversationDetailResponse:
    """
    Retrieve a specific conversation along with all associated messages.
    """
    stmt = (
        select(Conversation)
        .options(selectinload(Conversation.messages))
        .where(Conversation.id == conversation_id)
    )
    result = await db.execute(stmt)
    conv = result.scalar_one_or_none()

    if not conv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation with ID '{conversation_id}' was not found.",
        )

    formatted_messages = [
        MessageResponse(
            id=m.id,
            conversation_id=m.conversation_id,
            role=m.role,
            content=m.content,
            metadata=m.msg_metadata,
            created_at=m.created_at,
        )
        for m in sorted(conv.messages, key=lambda x: x.created_at)
    ]

    return ConversationDetailResponse(
        id=conv.id,
        title=conv.title,
        created_at=conv.created_at,
        updated_at=conv.updated_at,
        messages=formatted_messages,
    )


@router.delete(
    "/conversations/{conversation_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a conversation",
)
async def delete_conversation(
    conversation_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Delete a conversation and all cascading message records.
    """
    stmt = select(Conversation).where(Conversation.id == conversation_id)
    result = await db.execute(stmt)
    conv = result.scalar_one_or_none()

    if not conv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation with ID '{conversation_id}' was not found.",
        )

    await db.delete(conv)
    await db.commit()

    return {
        "status": "success",
        "message": f"Conversation '{conversation_id}' deleted successfully.",
        "id": str(conversation_id),
    }
