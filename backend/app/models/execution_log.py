"""Execution log database model."""

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database import Base

if TYPE_CHECKING:
    from backend.app.models.conversation import Conversation


class ExecutionLog(Base):
    """Model for storing execution logs and events.

    Tracks all execution events including function calls, errors,
    LLM calls, and general messages for debugging and monitoring.
    """

    __tablename__ = "execution_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4, index=True
    )
    conversation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    event_type: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )  # 'function_call', 'error', 'llm_call', 'message', 'system'
    level: Mapped[str] = mapped_column(
        String(20), nullable=False, default="info", index=True
    )  # 'debug', 'info', 'warning', 'error'
    agent_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    data: Mapped[dict | None] = mapped_column(
        JSON, nullable=True
    )  # Additional structured data (tokens, execution time, function args, etc.)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )

    # Relationship
    conversation: Mapped["Conversation"] = relationship(
        "Conversation", back_populates="logs"
    )

    # Composite indexes for common query patterns
    __table_args__ = (
        Index("idx_conversation_timestamp", "conversation_id", "timestamp"),
        Index("idx_conversation_level", "conversation_id", "level"),
        Index("idx_conversation_event_type", "conversation_id", "event_type"),
    )

    def __repr__(self) -> str:
        return (
            f"<ExecutionLog(id={self.id}, "
            f"event_type={self.event_type}, level={self.level})>"
        )
