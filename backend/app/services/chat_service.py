"""Chat service with business logic."""

from uuid import UUID

from sqlalchemy.orm import Session

from backend.app import models, schemas


def create_conversation(
    db: Session, conversation_data: schemas.ConversationCreate
) -> models.Conversation:
    """
    Create a new conversation.

    Args:
        db: Database session
        conversation_data: Conversation creation data

    Returns:
        Created conversation model
    """
    conversation = models.Conversation(
        agent_id=conversation_data.agent_id,
        agent_version_id=conversation_data.agent_version_id,
        title=conversation_data.title,
        extra_data=conversation_data.extra_data,
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation


def list_conversations(
    db: Session, skip: int = 0, limit: int = 100
) -> list[models.Conversation]:
    """
    List all conversations with pagination.

    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        List of conversations
    """
    return db.query(models.Conversation).offset(skip).limit(limit).all()


def get_conversation(db: Session, conversation_id: UUID) -> models.Conversation | None:
    """
    Get conversation by ID.

    Args:
        db: Database session
        conversation_id: Conversation ID

    Returns:
        Conversation model or None if not found
    """
    return (
        db.query(models.Conversation)
        .filter(models.Conversation.id == conversation_id)
        .first()
    )


def create_message(
    db: Session, conversation_id: UUID, message_data: schemas.MessageCreate
) -> models.Message | None:
    """
    Create a new message in a conversation.

    Args:
        db: Database session
        conversation_id: Conversation ID
        message_data: Message creation data

    Returns:
        Created message or None if conversation not found
    """
    conversation = get_conversation(db, conversation_id)
    if not conversation:
        return None

    message = models.Message(
        conversation_id=conversation_id,
        role=message_data.role,
        content=message_data.content,
        extra_data=message_data.extra_data,
        parent_message_id=message_data.parent_message_id,
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def list_messages(db: Session, conversation_id: UUID) -> list[models.Message]:
    """
    List all messages in a conversation.

    Args:
        db: Database session
        conversation_id: Conversation ID

    Returns:
        List of messages
    """
    return (
        db.query(models.Message)
        .filter(models.Message.conversation_id == conversation_id)
        .order_by(models.Message.created_at)
        .all()
    )
