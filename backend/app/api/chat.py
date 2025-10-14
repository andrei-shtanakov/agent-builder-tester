"""Chat API endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from backend.app import models, schemas
from backend.app.database import get_db
from backend.app.middleware.rate_limit import limiter
from backend.app.services import chat_service

router = APIRouter()


@router.post(
    "/sessions",
    response_model=schemas.Conversation,
    status_code=status.HTTP_201_CREATED,
)
def create_conversation(
    conversation_data: schemas.ConversationCreate, db: Session = Depends(get_db)
) -> models.Conversation:
    """Create a new chat conversation."""
    return chat_service.create_conversation(db, conversation_data)


@router.get("/sessions", response_model=list[schemas.Conversation])
def list_conversations(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
) -> list[models.Conversation]:
    """List all conversations with pagination."""
    return chat_service.list_conversations(db, skip=skip, limit=limit)


@router.get("/sessions/{conversation_id}", response_model=schemas.Conversation)
def get_conversation(
    conversation_id: UUID, db: Session = Depends(get_db)
) -> models.Conversation:
    """Get conversation by ID."""
    conversation = chat_service.get_conversation(db, conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found"
        )
    return conversation


@router.post(
    "/sessions/{conversation_id}/messages",
    response_model=schemas.Message,
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit("30/minute")
def create_message(
    request: Request,
    conversation_id: UUID,
    message_data: schemas.MessageCreate,
    db: Session = Depends(get_db),
) -> models.Message:
    """Create a new message in a conversation."""
    message = chat_service.create_message(db, conversation_id, message_data)
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found"
        )
    return message


@router.get(
    "/sessions/{conversation_id}/messages", response_model=list[schemas.Message]
)
def list_messages(
    conversation_id: UUID, db: Session = Depends(get_db)
) -> list[models.Message]:
    """List all messages in a conversation."""
    return chat_service.list_messages(db, conversation_id)
