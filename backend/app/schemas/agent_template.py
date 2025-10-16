"""Agent template schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class AgentTemplateBase(BaseModel):
    """Base agent template schema."""

    name: str = Field(..., min_length=1, max_length=255, description="Template name")
    description: str | None = Field(None, description="Template description")
    category: str = Field(..., description="Template category")
    config: dict = Field(..., description="Template configuration")
    is_public: bool = Field(default=True, description="Is template public")


class AgentTemplateCreate(AgentTemplateBase):
    """Agent template creation schema."""

    pass


class AgentTemplateUpdate(BaseModel):
    """Agent template update schema."""

    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    category: str | None = None
    config: dict | None = None
    is_public: bool | None = None


class AgentTemplate(AgentTemplateBase):
    """Agent template response schema."""

    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
