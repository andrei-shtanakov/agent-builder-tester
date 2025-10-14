"""Agent service with business logic."""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from backend.app import models, schemas


def create_agent(db: Session, agent_data: schemas.AgentCreate) -> models.Agent:
    """
    Create a new agent.

    Args:
        db: Database session
        agent_data: Agent creation data

    Returns:
        Created agent model
    """
    agent = models.Agent(
        name=agent_data.name,
        description=agent_data.description,
        type=agent_data.type,
        status=agent_data.status,
        tags=agent_data.tags,
    )
    db.add(agent)
    db.flush()

    # Create initial version if config provided
    if agent_data.initial_config:
        version = models.AgentVersion(
            agent_id=agent.id,
            version="1.0.0",
            config=agent_data.initial_config,
            changelog="Initial version",
            is_current=True,
        )
        db.add(version)
        db.flush()
        agent.current_version_id = version.id

    db.commit()
    db.refresh(agent)
    return agent


def list_agents(db: Session, skip: int = 0, limit: int = 100) -> list[models.Agent]:
    """
    List all agents with pagination.

    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        List of agents
    """
    return db.query(models.Agent).offset(skip).limit(limit).all()


def get_agent(db: Session, agent_id: UUID) -> models.Agent | None:
    """
    Get agent by ID.

    Args:
        db: Database session
        agent_id: Agent ID

    Returns:
        Agent model or None if not found
    """
    return db.query(models.Agent).filter(models.Agent.id == agent_id).first()


def update_agent(
    db: Session, agent_id: UUID, agent_data: schemas.AgentUpdate
) -> models.Agent | None:
    """
    Update agent.

    Args:
        db: Database session
        agent_id: Agent ID
        agent_data: Update data

    Returns:
        Updated agent or None if not found
    """
    agent = get_agent(db, agent_id)
    if not agent:
        return None

    update_data = agent_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(agent, field, value)

    agent.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(agent)
    return agent


def delete_agent(db: Session, agent_id: UUID) -> bool:
    """
    Delete agent.

    Args:
        db: Database session
        agent_id: Agent ID

    Returns:
        True if deleted, False if not found
    """
    agent = get_agent(db, agent_id)
    if not agent:
        return False

    db.delete(agent)
    db.commit()
    return True
