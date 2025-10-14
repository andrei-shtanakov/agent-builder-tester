"""Group chat service with business logic."""

from uuid import UUID

from sqlalchemy.orm import Session

from backend.app import models, schemas


def create_group_chat(
    db: Session, group_chat_data: schemas.GroupChatCreate
) -> models.GroupChat:
    """
    Create a new group chat with participants.

    Args:
        db: Database session
        group_chat_data: Group chat creation data

    Returns:
        Created group chat model
    """
    group_chat = models.GroupChat(
        title=group_chat_data.title,
        description=group_chat_data.description,
        selection_strategy=group_chat_data.selection_strategy,
        max_rounds=group_chat_data.max_rounds,
        allow_repeated_speaker=group_chat_data.allow_repeated_speaker,
        termination_config=group_chat_data.termination_config,
        extra_data=group_chat_data.extra_data,
    )
    db.add(group_chat)
    db.flush()

    for agent_id in group_chat_data.participant_agent_ids:
        participant = models.GroupChatParticipant(
            group_chat_id=group_chat.id,
            agent_id=agent_id,
        )
        db.add(participant)

    db.commit()
    db.refresh(group_chat)
    return group_chat


def list_group_chats(
    db: Session, skip: int = 0, limit: int = 100
) -> list[models.GroupChat]:
    """
    List all group chats with pagination.

    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        List of group chats
    """
    return db.query(models.GroupChat).offset(skip).limit(limit).all()


def get_group_chat(db: Session, group_chat_id: UUID) -> models.GroupChat | None:
    """
    Get group chat by ID.

    Args:
        db: Database session
        group_chat_id: Group chat ID

    Returns:
        Group chat model or None if not found
    """
    return (
        db.query(models.GroupChat).filter(models.GroupChat.id == group_chat_id).first()
    )


def update_group_chat(
    db: Session, group_chat_id: UUID, update_data: schemas.GroupChatUpdate
) -> models.GroupChat | None:
    """
    Update group chat.

    Args:
        db: Database session
        group_chat_id: Group chat ID
        update_data: Update data

    Returns:
        Updated group chat or None if not found
    """
    group_chat = get_group_chat(db, group_chat_id)
    if not group_chat:
        return None

    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(group_chat, key, value)

    db.commit()
    db.refresh(group_chat)
    return group_chat


def delete_group_chat(db: Session, group_chat_id: UUID) -> bool:
    """
    Delete group chat.

    Args:
        db: Database session
        group_chat_id: Group chat ID

    Returns:
        True if deleted, False if not found
    """
    group_chat = get_group_chat(db, group_chat_id)
    if not group_chat:
        return False

    db.delete(group_chat)
    db.commit()
    return True


def add_participant(
    db: Session,
    group_chat_id: UUID,
    participant_data: schemas.GroupChatParticipantCreate,
) -> models.GroupChatParticipant | None:
    """
    Add a participant to group chat.

    Args:
        db: Database session
        group_chat_id: Group chat ID
        participant_data: Participant data

    Returns:
        Created participant or None if group chat not found
    """
    group_chat = get_group_chat(db, group_chat_id)
    if not group_chat:
        return None

    participant = models.GroupChatParticipant(
        group_chat_id=group_chat_id,
        agent_id=participant_data.agent_id,
        agent_version_id=participant_data.agent_version_id,
        speaking_order=participant_data.speaking_order,
        constraints=participant_data.constraints,
    )
    db.add(participant)
    db.commit()
    db.refresh(participant)
    return participant


def remove_participant(db: Session, group_chat_id: UUID, agent_id: UUID) -> bool:
    """
    Remove a participant from group chat.

    Args:
        db: Database session
        group_chat_id: Group chat ID
        agent_id: Agent ID to remove

    Returns:
        True if removed, False if not found
    """
    participant = (
        db.query(models.GroupChatParticipant)
        .filter(
            models.GroupChatParticipant.group_chat_id == group_chat_id,
            models.GroupChatParticipant.agent_id == agent_id,
        )
        .first()
    )

    if not participant:
        return False

    db.delete(participant)
    db.commit()
    return True


def list_participants(
    db: Session, group_chat_id: UUID
) -> list[models.GroupChatParticipant]:
    """
    List all participants in a group chat.

    Args:
        db: Database session
        group_chat_id: Group chat ID

    Returns:
        List of participants
    """
    return (
        db.query(models.GroupChatParticipant)
        .filter(models.GroupChatParticipant.group_chat_id == group_chat_id)
        .order_by(models.GroupChatParticipant.speaking_order)
        .all()
    )


def list_group_chat_messages(
    db: Session, group_chat_id: UUID
) -> list[models.Message]:
    """
    List all messages for conversations linked to a group chat.

    Args:
        db: Database session
        group_chat_id: Group chat identifier

    Returns:
        Messages ordered by creation time across all related conversations
    """
    conversation_links = (
        db.query(models.GroupChatConversation)
        .filter(models.GroupChatConversation.group_chat_id == group_chat_id)
        .all()
    )

    conversation_ids = [link.conversation_id for link in conversation_links]
    if not conversation_ids:
        return []

    return (
        db.query(models.Message)
        .filter(models.Message.conversation_id.in_(conversation_ids))
        .order_by(models.Message.created_at)
        .all()
    )
