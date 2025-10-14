"""Group chat schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class GroupChatParticipantBase(BaseModel):
    """Base group chat participant schema."""

    agent_id: UUID = Field(..., description="Agent ID")
    agent_version_id: UUID | None = Field(None, description="Agent version ID")
    speaking_order: int | None = Field(
        None, description="Order in round-robin (optional)"
    )
    constraints: dict | None = Field(None, description="Speaking constraints")


class GroupChatParticipantCreate(GroupChatParticipantBase):
    """Group chat participant creation schema."""

    pass


class GroupChatParticipant(GroupChatParticipantBase):
    """Group chat participant response schema."""

    id: UUID
    group_chat_id: UUID
    added_at: datetime

    model_config = {"from_attributes": True}


class GroupChatBase(BaseModel):
    """Base group chat schema."""

    title: str = Field(..., min_length=1, max_length=255, description="Chat title")
    description: str | None = Field(None, description="Chat description")
    selection_strategy: str = Field(
        default="selector",
        description="Speaker selection strategy (selector, round_robin, swarm)",
    )
    max_rounds: int = Field(
        default=10, ge=1, le=100, description="Maximum conversation rounds"
    )
    allow_repeated_speaker: bool = Field(
        default=False, description="Allow same agent to speak consecutively"
    )
    termination_config: dict | None = Field(None, description="Termination conditions")
    extra_data: dict | None = Field(None, description="Additional metadata")


class GroupChatCreate(GroupChatBase):
    """Group chat creation schema."""

    participant_agent_ids: list[UUID] = Field(
        ..., min_length=2, description="Initial participant agent IDs (min 2)"
    )


class GroupChatUpdate(BaseModel):
    """Group chat update schema."""

    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    selection_strategy: str | None = None
    max_rounds: int | None = Field(None, ge=1, le=100)
    allow_repeated_speaker: bool | None = None
    termination_config: dict | None = None
    extra_data: dict | None = None
    status: str | None = None


class GroupChat(GroupChatBase):
    """Group chat response schema."""

    id: UUID
    status: str
    created_at: datetime
    updated_at: datetime
    participants: list[GroupChatParticipant] = []

    model_config = {"from_attributes": True}


class GroupChatMessageCreate(BaseModel):
    """Message to send to group chat."""

    content: str = Field(..., description="Message content")
    sender_type: str = Field(default="user", description="Sender type (user, system)")
    extra_data: dict | None = Field(None, description="Additional metadata")


class GroupChatConversationBase(BaseModel):
    """Base group chat conversation schema."""

    round_number: int = Field(..., description="Current round number")
    current_speaker_agent_id: UUID | None = Field(
        None, description="Current speaker agent"
    )
    extra_data: dict | None = Field(None, description="Additional metadata")


class GroupChatConversation(GroupChatConversationBase):
    """Group chat conversation response schema."""

    id: UUID
    group_chat_id: UUID
    conversation_id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}
