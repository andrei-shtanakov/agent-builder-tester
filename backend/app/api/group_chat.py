"""Group chat API endpoints."""

from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from backend.app import models, schemas
from backend.app.autogen_integration.group_chat_manager import run_group_chat
from backend.app.database import get_db
from backend.app.middleware.rate_limit import limiter
from backend.app.services import chat_service, group_chat_service

router = APIRouter()


@router.post(
    "",
    response_model=schemas.GroupChat,
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit("10/minute")
def create_group_chat(
    request: Request,
    group_chat_data: schemas.GroupChatCreate,
    db: Session = Depends(get_db),
) -> models.GroupChat:
    """Create a new group chat."""
    return group_chat_service.create_group_chat(db, group_chat_data)


@router.get("", response_model=list[schemas.GroupChat])
def list_group_chats(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
) -> list[models.GroupChat]:
    """List all group chats with pagination."""
    return group_chat_service.list_group_chats(db, skip=skip, limit=limit)


@router.get("/{group_chat_id}", response_model=schemas.GroupChat)
def get_group_chat(
    group_chat_id: UUID, db: Session = Depends(get_db)
) -> models.GroupChat:
    """Get group chat by ID."""
    group_chat = group_chat_service.get_group_chat(db, group_chat_id)
    if not group_chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Group chat not found"
        )
    return group_chat


@router.put("/{group_chat_id}", response_model=schemas.GroupChat)
@limiter.limit("10/minute")
def update_group_chat(
    request: Request,
    group_chat_id: UUID,
    update_data: schemas.GroupChatUpdate,
    db: Session = Depends(get_db),
) -> models.GroupChat:
    """Update group chat."""
    group_chat = group_chat_service.update_group_chat(db, group_chat_id, update_data)
    if not group_chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Group chat not found"
        )
    return group_chat


@router.delete("/{group_chat_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("10/minute")
def delete_group_chat(
    request: Request, group_chat_id: UUID, db: Session = Depends(get_db)
) -> None:
    """Delete group chat."""
    success = group_chat_service.delete_group_chat(db, group_chat_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Group chat not found"
        )


@router.post(
    "/{group_chat_id}/participants",
    response_model=schemas.GroupChatParticipant,
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit("10/minute")
def add_participant(
    request: Request,
    group_chat_id: UUID,
    participant_data: schemas.GroupChatParticipantCreate,
    db: Session = Depends(get_db),
) -> models.GroupChatParticipant:
    """Add a participant to group chat."""
    participant = group_chat_service.add_participant(
        db, group_chat_id, participant_data
    )
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Group chat not found"
        )
    return participant


@router.delete(
    "/{group_chat_id}/participants/{agent_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
@limiter.limit("10/minute")
def remove_participant(
    request: Request,
    group_chat_id: UUID,
    agent_id: UUID,
    db: Session = Depends(get_db),
) -> None:
    """Remove a participant from group chat."""
    success = group_chat_service.remove_participant(db, group_chat_id, agent_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Participant not found in group chat",
        )


@router.get(
    "/{group_chat_id}/participants",
    response_model=list[schemas.GroupChatParticipant],
)
def list_participants(
    group_chat_id: UUID, db: Session = Depends(get_db)
) -> list[models.GroupChatParticipant]:
    """List all participants in a group chat."""
    return group_chat_service.list_participants(db, group_chat_id)


@router.get("/{group_chat_id}/messages", response_model=list[schemas.Message])
def list_group_chat_messages(
    group_chat_id: UUID, db: Session = Depends(get_db)
) -> list[schemas.Message]:
    """List all messages associated with a group chat."""
    messages = group_chat_service.list_group_chat_messages(db, group_chat_id)
    return [schemas.Message.model_validate(message) for message in messages]


@router.post(
    "/{group_chat_id}/start",
    response_model=schemas.Conversation,
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit("30/minute")
async def start_group_conversation(
    request: Request,
    group_chat_id: UUID,
    message_data: schemas.GroupChatMessageCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> models.Conversation:
    """
    Start a group chat conversation.

    This endpoint creates a conversation and initiates the group chat with
    the provided message. The group chat orchestration runs in the background.
    """
    group_chat = group_chat_service.get_group_chat(db, group_chat_id)
    if not group_chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Group chat not found"
        )

    participants = group_chat_service.list_participants(db, group_chat_id)
    if not participants:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Group chat has no participants",
        )

    conversation = chat_service.create_conversation(
        db,
        schemas.ConversationCreate(
            agent_id=participants[0].agent_id,
            title=f"Group Chat: {group_chat.title}",
            extra_data={"group_chat_id": str(group_chat_id)},
        ),
    )

    initial_message = chat_service.create_message(
        db,
        conversation.id,
        schemas.MessageCreate(
            role=message_data.sender_type,
            content=message_data.content,
            extra_data=message_data.extra_data,
        ),
    )

    if not initial_message:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create initial message",
        )

    background_tasks.add_task(
        run_group_chat,
        db,
        group_chat_id,
        message_data.content,
        conversation.id,
        None,
    )

    return conversation
