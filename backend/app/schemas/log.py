"""Execution log Pydantic schemas."""

from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


class LogLevel(str, Enum):
    """Log level enumeration."""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class EventType(str, Enum):
    """Event type enumeration."""

    MESSAGE = "message"
    FUNCTION_CALL = "function_call"
    LLM_CALL = "llm_call"
    ERROR = "error"
    SYSTEM = "system"


class ExecutionLogBase(BaseModel):
    """Base execution log schema."""

    event_type: EventType = Field(..., description="Type of event")
    level: LogLevel = Field(LogLevel.INFO, description="Log level")
    agent_name: str | None = Field(None, description="Name of the agent")
    content: str = Field(..., description="Log message content")
    data: dict | None = Field(
        None, description="Additional structured data (tokens, execution time, etc.)"
    )


class ExecutionLogCreate(ExecutionLogBase):
    """Schema for creating execution log."""

    conversation_id: UUID = Field(..., description="ID of the conversation")


class ExecutionLog(ExecutionLogBase):
    """Schema for execution log response."""

    id: UUID
    conversation_id: UUID
    timestamp: datetime

    model_config = {"from_attributes": True}


class LogFilter(BaseModel):
    """Schema for filtering logs."""

    level: LogLevel | None = Field(None, description="Filter by log level")
    event_type: EventType | None = Field(None, description="Filter by event type")
    agent_name: str | None = Field(None, description="Filter by agent name")
    start_time: datetime | None = Field(None, description="Filter logs after this time")
    end_time: datetime | None = Field(None, description="Filter logs before this time")
    limit: int = Field(100, ge=1, le=1000, description="Maximum number of logs")
    offset: int = Field(0, ge=0, description="Number of logs to skip")


class LogExportFormat(str, Enum):
    """Log export format enumeration."""

    JSON = "json"
    TXT = "txt"
    CSV = "csv"


class LogStats(BaseModel):
    """Schema for log statistics."""

    total_logs: int = Field(..., description="Total number of logs")
    by_level: dict[str, int] = Field(..., description="Count of logs by level")
    by_event_type: dict[str, int] = Field(
        ..., description="Count of logs by event type"
    )
    time_range: dict[str, datetime | None] = Field(
        ..., description="Time range of logs (start, end)"
    )
