"""Logs API endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from backend.app import models, schemas
from backend.app.database import get_db
from backend.app.services import log_service

router = APIRouter()


@router.post(
    "/",
    response_model=schemas.ExecutionLog,
    status_code=status.HTTP_201_CREATED,
)
def create_log(
    log_data: schemas.ExecutionLogCreate, db: Session = Depends(get_db)
) -> models.ExecutionLog:
    """Create a new execution log entry."""
    return log_service.create_log(db, log_data)


@router.get("/sessions/{conversation_id}", response_model=list[schemas.ExecutionLog])
def get_session_logs(
    conversation_id: UUID,
    level: schemas.LogLevel | None = Query(None, description="Filter by log level"),
    event_type: schemas.EventType | None = Query(
        None, description="Filter by event type"
    ),
    agent_name: str | None = Query(None, description="Filter by agent name"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of logs"),
    offset: int = Query(0, ge=0, description="Number of logs to skip"),
    db: Session = Depends(get_db),
) -> list[models.ExecutionLog]:
    """Get execution logs for a conversation with optional filtering."""
    filter_params = schemas.LogFilter(
        level=level,
        event_type=event_type,
        agent_name=agent_name,
        limit=limit,
        offset=offset,
    )
    return log_service.get_logs(db, conversation_id, filter_params)


@router.get("/sessions/{conversation_id}/stats", response_model=schemas.LogStats)
def get_session_stats(
    conversation_id: UUID, db: Session = Depends(get_db)
) -> schemas.LogStats:
    """Get statistics for logs in a conversation."""
    return log_service.get_log_stats(db, conversation_id)


@router.get(
    "/sessions/{conversation_id}/export",
    response_class=PlainTextResponse,
)
def export_session_logs(
    conversation_id: UUID,
    format: schemas.LogExportFormat = Query(
        schemas.LogExportFormat.JSON, description="Export format (json, txt, csv)"
    ),
    level: schemas.LogLevel | None = Query(None, description="Filter by log level"),
    event_type: schemas.EventType | None = Query(
        None, description="Filter by event type"
    ),
    agent_name: str | None = Query(None, description="Filter by agent name"),
    limit: int = Query(1000, ge=1, le=10000, description="Maximum number of logs"),
    offset: int = Query(0, ge=0, description="Number of logs to skip"),
    db: Session = Depends(get_db),
) -> str:
    """Export logs for a conversation in the specified format."""
    filter_params = schemas.LogFilter(
        level=level,
        event_type=event_type,
        agent_name=agent_name,
        limit=limit,
        offset=offset,
    )
    return log_service.export_logs(db, conversation_id, format, filter_params)


@router.delete(
    "/sessions/{conversation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_session_logs(conversation_id: UUID, db: Session = Depends(get_db)) -> None:
    """Delete all logs for a conversation."""
    count = log_service.delete_logs(db, conversation_id)
    if count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No logs found for this conversation",
        )


@router.get("/{log_id}", response_model=schemas.ExecutionLog)
def get_log(log_id: UUID, db: Session = Depends(get_db)) -> models.ExecutionLog:
    """Get a specific log entry by ID."""
    log = log_service.get_log(db, log_id)
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Log not found"
        )
    return log
