"""Group chat database models."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database import Base


class GroupChat(Base):
    """Group chat model for multi-agent conversations."""

    __tablename__ = "group_chats"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    selection_strategy: Mapped[str] = mapped_column(
        String(50), nullable=False, default="selector"
    )
    max_rounds: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    allow_repeated_speaker: Mapped[bool] = mapped_column(nullable=False, default=False)
    termination_config: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    extra_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")

    # Relationships
    participants: Mapped[list["GroupChatParticipant"]] = relationship(
        "GroupChatParticipant",
        back_populates="group_chat",
        cascade="all, delete-orphan",
    )
    conversations: Mapped[list["GroupChatConversation"]] = relationship(
        "GroupChatConversation",
        back_populates="group_chat",
        cascade="all, delete-orphan",
    )


class GroupChatParticipant(Base):
    """Participant in a group chat (agent)."""

    __tablename__ = "group_chat_participants"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4, index=True
    )
    group_chat_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("group_chats.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    agent_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("agents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    agent_version_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("agent_versions.id", ondelete="SET NULL"),
        nullable=True,
    )
    speaking_order: Mapped[int | None] = mapped_column(Integer, nullable=True)
    constraints: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    added_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    group_chat: Mapped["GroupChat"] = relationship(
        "GroupChat", back_populates="participants"
    )


class GroupChatConversation(Base):
    """Conversation within a group chat."""

    __tablename__ = "group_chat_conversations"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4, index=True
    )
    group_chat_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("group_chats.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    conversation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    round_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    current_speaker_agent_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("agents.id", ondelete="SET NULL"),
        nullable=True,
    )
    extra_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    group_chat: Mapped["GroupChat"] = relationship(
        "GroupChat", back_populates="conversations"
    )
