"""Agent template service with business logic."""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from backend.app import schemas
from backend.app.models.agent_template import AgentTemplate


def create_template(
    db: Session, template_data: schemas.AgentTemplateCreate
) -> AgentTemplate:
    """
    Create a new agent template.

    Args:
        db: Database session
        template_data: Template creation data

    Returns:
        Created template model
    """
    template = AgentTemplate(
        name=template_data.name,
        description=template_data.description,
        category=template_data.category,
        config=template_data.config,
        is_public=template_data.is_public,
    )
    db.add(template)
    db.commit()
    db.refresh(template)
    return template


def list_templates(
    db: Session, skip: int = 0, limit: int = 100, category: str | None = None
) -> list[AgentTemplate]:
    """
    List all agent templates with pagination and optional filtering.

    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        category: Optional category filter

    Returns:
        List of templates
    """
    query = db.query(AgentTemplate).filter(AgentTemplate.is_public.is_(True))
    if category:
        query = query.filter(AgentTemplate.category == category)
    return query.offset(skip).limit(limit).all()


def get_template(db: Session, template_id: UUID) -> AgentTemplate | None:
    """
    Get template by ID.

    Args:
        db: Database session
        template_id: Template ID

    Returns:
        Template model or None if not found
    """
    return db.query(AgentTemplate).filter(AgentTemplate.id == template_id).first()


def update_template(
    db: Session, template_id: UUID, template_data: schemas.AgentTemplateUpdate
) -> AgentTemplate | None:
    """
    Update template.

    Args:
        db: Database session
        template_id: Template ID
        template_data: Update data

    Returns:
        Updated template or None if not found
    """
    template = get_template(db, template_id)
    if not template:
        return None

    update_data = template_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(template, field, value)

    template.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(template)
    return template


def delete_template(db: Session, template_id: UUID) -> bool:
    """
    Delete template.

    Args:
        db: Database session
        template_id: Template ID

    Returns:
        True if deleted, False if not found
    """
    template = get_template(db, template_id)
    if not template:
        return False

    db.delete(template)
    db.commit()
    return True


def seed_default_templates(db: Session) -> None:
    """
    Seed database with default agent templates.

    Args:
        db: Database session
    """
    default_templates = [
        {
            "name": "Customer Support Agent",
            "description": "Helpful customer support agent",
            "category": "support",
            "config": {
                "system_message": (
                    "You are a helpful customer support agent. "
                    "Provide clear, friendly assistance to customers."
                ),
                "temperature": 0.7,
                "max_tokens": 1000,
            },
        },
        {
            "name": "Code Review Agent",
            "description": "Agent that reviews code and suggests improvements",
            "category": "development",
            "config": {
                "system_message": (
                    "You are a code review expert. "
                    "Analyze code and provide constructive feedback."
                ),
                "temperature": 0.3,
                "max_tokens": 2000,
            },
        },
        {
            "name": "Data Analyst Agent",
            "description": "Agent that analyzes data and provides insights",
            "category": "analytics",
            "config": {
                "system_message": (
                    "You are a data analyst. Analyze data and provide clear insights."
                ),
                "temperature": 0.5,
                "max_tokens": 1500,
            },
        },
    ]

    for template_data in default_templates:
        existing = (
            db.query(AgentTemplate)
            .filter(AgentTemplate.name == template_data["name"])
            .first()
        )
        if not existing:
            template = AgentTemplate(**template_data, is_public=True)
            db.add(template)

    db.commit()
