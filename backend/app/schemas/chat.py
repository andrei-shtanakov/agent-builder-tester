"""Chat schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class MessageBase(BaseModel):
    """Base message schema."""

    role: str = Field(..., description="Message role (user, assistant, system)")
    content: str = Field(..., description="Message content")
    extra_data: dict | None = Field(None, description="Additional metadata")


class MessageCreate(MessageBase):
    """Message creation schema."""

    parent_message_id: UUID | None = Field(None, description="Parent message ID")


class Message(MessageBase):
    """Message response schema."""

    id: UUID
    conversation_id: UUID
    created_at: datetime
    parent_message_id: UUID | None

    model_config = {"from_attributes": True}


class ConversationBase(BaseModel):
    """Base conversation schema."""

    title: str | None = Field(None, max_length=255, description="Conversation title")
    extra_data: dict | None = Field(None, description="Additional metadata")


class ConversationCreate(ConversationBase):
    """Conversation creation schema."""

    agent_id: UUID = Field(..., description="Agent ID")
    agent_version_id: UUID | None = Field(None, description="Agent version ID")


class Conversation(ConversationBase):
    """Conversation response schema."""

    id: UUID
    agent_id: UUID
    agent_version_id: UUID | None
    started_at: datetime
    ended_at: datetime | None
    status: str
    messages: list[Message] = []

    model_config = {"from_attributes": True}
