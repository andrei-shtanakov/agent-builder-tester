"""Agent API endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from backend.app import models, schemas
from backend.app.database import get_db
from backend.app.middleware.rate_limit import limiter
from backend.app.services import agent_service

router = APIRouter()


@router.post("/", response_model=schemas.Agent, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
def create_agent(
    request: Request, agent_data: schemas.AgentCreate, db: Session = Depends(get_db)
) -> models.Agent:
    """Create a new agent."""
    return agent_service.create_agent(db, agent_data)


@router.get("/", response_model=list[schemas.Agent])
def list_agents(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
) -> list[models.Agent]:
    """List all agents with pagination."""
    return agent_service.list_agents(db, skip=skip, limit=limit)


@router.get("/{agent_id}", response_model=schemas.Agent)
def get_agent(agent_id: UUID, db: Session = Depends(get_db)) -> models.Agent:
    """Get agent by ID."""
    agent = agent_service.get_agent(db, agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found"
        )
    return agent


@router.put("/{agent_id}", response_model=schemas.Agent)
@limiter.limit("10/minute")
def update_agent(
    request: Request,
    agent_id: UUID,
    agent_data: schemas.AgentUpdate,
    db: Session = Depends(get_db),
) -> models.Agent:
    """Update agent."""
    agent = agent_service.update_agent(db, agent_id, agent_data)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found"
        )
    return agent


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("10/minute")
def delete_agent(
    request: Request, agent_id: UUID, db: Session = Depends(get_db)
) -> None:
    """Delete agent."""
    success = agent_service.delete_agent(db, agent_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found"
        )
