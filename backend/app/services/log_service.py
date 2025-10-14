"""Log service for managing execution logs."""

import csv
import json
from io import StringIO
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.app import models, schemas


def create_log(
    db: Session, log_data: schemas.ExecutionLogCreate
) -> models.ExecutionLog:
    """Create a new execution log entry.

    Args:
        db: Database session
        log_data: Log data to create

    Returns:
        Created execution log
    """
    db_log = models.ExecutionLog(
        conversation_id=log_data.conversation_id,
        event_type=log_data.event_type.value,
        level=log_data.level.value,
        agent_name=log_data.agent_name,
        content=log_data.content,
        data=log_data.data,
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log


def get_logs(
    db: Session, conversation_id: UUID, filter_params: schemas.LogFilter | None = None
) -> list[models.ExecutionLog]:
    """Get logs for a conversation with optional filtering.

    Args:
        db: Database session
        conversation_id: ID of the conversation
        filter_params: Optional filter parameters

    Returns:
        List of execution logs
    """
    query = db.query(models.ExecutionLog).filter(
        models.ExecutionLog.conversation_id == conversation_id
    )

    if filter_params:
        if filter_params.level:
            query = query.filter(models.ExecutionLog.level == filter_params.level.value)
        if filter_params.event_type:
            query = query.filter(
                models.ExecutionLog.event_type == filter_params.event_type.value
            )
        if filter_params.agent_name:
            query = query.filter(
                models.ExecutionLog.agent_name == filter_params.agent_name
            )
        if filter_params.start_time:
            query = query.filter(
                models.ExecutionLog.timestamp >= filter_params.start_time
            )
        if filter_params.end_time:
            query = query.filter(
                models.ExecutionLog.timestamp <= filter_params.end_time
            )

        query = query.order_by(models.ExecutionLog.timestamp.desc())
        query = query.offset(filter_params.offset).limit(filter_params.limit)
    else:
        query = query.order_by(models.ExecutionLog.timestamp.desc()).limit(100)

    return query.all()


def get_log(db: Session, log_id: UUID) -> models.ExecutionLog | None:
    """Get a specific log entry by ID.

    Args:
        db: Database session
        log_id: ID of the log entry

    Returns:
        Log entry or None if not found
    """
    return (
        db.query(models.ExecutionLog).filter(models.ExecutionLog.id == log_id).first()
    )


def delete_logs(db: Session, conversation_id: UUID) -> int:
    """Delete all logs for a conversation.

    Args:
        db: Database session
        conversation_id: ID of the conversation

    Returns:
        Number of logs deleted
    """
    count = (
        db.query(models.ExecutionLog)
        .filter(models.ExecutionLog.conversation_id == conversation_id)
        .delete()
    )
    db.commit()
    return count


def get_log_stats(db: Session, conversation_id: UUID) -> schemas.LogStats:
    """Get statistics for logs in a conversation.

    Args:
        db: Database session
        conversation_id: ID of the conversation

    Returns:
        Log statistics
    """
    # Total count
    total_logs = (
        db.query(func.count(models.ExecutionLog.id))
        .filter(models.ExecutionLog.conversation_id == conversation_id)
        .scalar()
        or 0
    )

    # Count by level
    level_counts = (
        db.query(models.ExecutionLog.level, func.count(models.ExecutionLog.id))
        .filter(models.ExecutionLog.conversation_id == conversation_id)
        .group_by(models.ExecutionLog.level)
        .all()
    )
    by_level = {level: count for level, count in level_counts}

    # Count by event type
    event_counts = (
        db.query(models.ExecutionLog.event_type, func.count(models.ExecutionLog.id))
        .filter(models.ExecutionLog.conversation_id == conversation_id)
        .group_by(models.ExecutionLog.event_type)
        .all()
    )
    by_event_type = {event: count for event, count in event_counts}

    # Time range
    time_range_query = db.query(
        func.min(models.ExecutionLog.timestamp), func.max(models.ExecutionLog.timestamp)
    ).filter(models.ExecutionLog.conversation_id == conversation_id)
    time_range_result = time_range_query.first()
    start_time, end_time = time_range_result if time_range_result else (None, None)

    return schemas.LogStats(
        total_logs=total_logs,
        by_level=by_level,
        by_event_type=by_event_type,
        time_range={"start": start_time, "end": end_time},
    )


def export_logs(
    db: Session,
    conversation_id: UUID,
    export_format: schemas.LogExportFormat,
    filter_params: schemas.LogFilter | None = None,
) -> str:
    """Export logs in the specified format.

    Args:
        db: Database session
        conversation_id: ID of the conversation
        export_format: Format for export (json, txt, csv)
        filter_params: Optional filter parameters

    Returns:
        Exported logs as string
    """
    logs = get_logs(db, conversation_id, filter_params)

    if export_format == schemas.LogExportFormat.JSON:
        return _export_json(logs)
    elif export_format == schemas.LogExportFormat.TXT:
        return _export_txt(logs)
    elif export_format == schemas.LogExportFormat.CSV:
        return _export_csv(logs)

    raise ValueError(f"Unsupported export format: {export_format}")


def _export_json(logs: list[models.ExecutionLog]) -> str:
    """Export logs as JSON."""
    log_dicts = [
        {
            "id": str(log.id),
            "conversation_id": str(log.conversation_id),
            "event_type": log.event_type,
            "level": log.level,
            "agent_name": log.agent_name,
            "content": log.content,
            "data": log.data,
            "timestamp": log.timestamp.isoformat(),
        }
        for log in logs
    ]
    return json.dumps(log_dicts, indent=2)


def _export_txt(logs: list[models.ExecutionLog]) -> str:
    """Export logs as plain text."""
    lines: list[str] = []
    for log in logs:
        timestamp = log.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        agent = f"[{log.agent_name}]" if log.agent_name else ""
        line = f"[{timestamp}] [{log.level.upper()}] [{log.event_type}] {agent} {log.content}"
        lines.append(line)
        if log.data:
            data_line = f"  Data: {json.dumps(log.data)}"
            lines.append(data_line)
        lines.append("")
    return "\n".join(lines)


def _export_csv(logs: list[models.ExecutionLog]) -> str:
    """Export logs as CSV."""
    output = StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow(
        [
            "Timestamp",
            "Level",
            "Event Type",
            "Agent Name",
            "Content",
            "Data",
        ]
    )

    # Write rows
    for log in logs:
        writer.writerow(
            [
                log.timestamp.isoformat(),
                log.level,
                log.event_type,
                log.agent_name or "",
                log.content,
                json.dumps(log.data) if log.data else "",
            ]
        )

    return output.getvalue()
