"""Agent schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class AgentVersionBase(BaseModel):
    """Base agent version schema."""

    version: str = Field(..., description="Version number (e.g., 1.0.0)")
    config: dict = Field(..., description="Agent configuration")
    changelog: str | None = Field(None, description="Changes in this version")
    created_by: str | None = Field(None, description="Creator identifier")


class AgentVersionCreate(AgentVersionBase):
    """Agent version creation schema."""

    pass


class AgentVersion(AgentVersionBase):
    """Agent version response schema."""

    id: UUID
    agent_id: UUID
    created_at: datetime
    is_current: bool

    model_config = {"from_attributes": True}


class AgentBase(BaseModel):
    """Base agent schema."""

    name: str = Field(..., min_length=1, max_length=255, description="Agent name")
    description: str | None = Field(None, description="Agent description")
    type: str = Field(..., description="Agent type")
    status: str = Field(default="draft", description="Agent status")
    tags: dict | None = Field(None, description="Agent tags")


class AgentCreate(AgentBase):
    """Agent creation schema."""

    initial_config: dict | None = Field(
        None, description="Initial configuration for first version"
    )


class AgentUpdate(BaseModel):
    """Agent update schema."""

    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    type: str | None = None
    status: str | None = None
    tags: dict | None = None


class Agent(AgentBase):
    """Agent response schema."""

    id: UUID
    current_version_id: UUID | None
    created_at: datetime
    updated_at: datetime
    versions: list[AgentVersion] = []

    model_config = {"from_attributes": True}
