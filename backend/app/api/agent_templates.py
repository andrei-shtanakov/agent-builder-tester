"""Agent template API endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from backend.app import schemas
from backend.app.database import get_db
from backend.app.middleware.rate_limit import limiter
from backend.app.models.agent_template import AgentTemplate
from backend.app.services import agent_template_service

router = APIRouter()


@router.post(
    "/", response_model=schemas.AgentTemplate, status_code=status.HTTP_201_CREATED
)
@limiter.limit("10/minute")
def create_template(
    request: Request,
    template_data: schemas.AgentTemplateCreate,
    db: Session = Depends(get_db),
) -> AgentTemplate:
    """Create a new agent template."""
    return agent_template_service.create_template(db, template_data)


@router.get("/", response_model=list[schemas.AgentTemplate])
def list_templates(
    skip: int = 0,
    limit: int = 100,
    category: str | None = None,
    db: Session = Depends(get_db),
) -> list[AgentTemplate]:
    """List all agent templates with pagination and optional filtering."""
    return agent_template_service.list_templates(
        db, skip=skip, limit=limit, category=category
    )


@router.get("/{template_id}", response_model=schemas.AgentTemplate)
def get_template(template_id: UUID, db: Session = Depends(get_db)) -> AgentTemplate:
    """Get template by ID."""
    template = agent_template_service.get_template(db, template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Template not found"
        )
    return template


@router.put("/{template_id}", response_model=schemas.AgentTemplate)
@limiter.limit("10/minute")
def update_template(
    request: Request,
    template_id: UUID,
    template_data: schemas.AgentTemplateUpdate,
    db: Session = Depends(get_db),
) -> AgentTemplate:
    """Update template."""
    template = agent_template_service.update_template(db, template_id, template_data)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Template not found"
        )
    return template


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("10/minute")
def delete_template(
    request: Request, template_id: UUID, db: Session = Depends(get_db)
) -> None:
    """Delete template."""
    success = agent_template_service.delete_template(db, template_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Template not found"
        )
