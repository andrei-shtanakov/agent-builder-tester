"""Tests for log service."""

import json

from backend.app import models, schemas
from backend.app.services import log_service


def test_create_log(db_session):
    """Test creating a log entry."""
    # Create conversation first
    agent = models.Agent(name="Test Agent", type="assistant", status="active")
    db_session.add(agent)
    db_session.flush()

    conversation = models.Conversation(
        agent_id=agent.id, title="Test Conversation", status="active"
    )
    db_session.add(conversation)
    db_session.commit()

    # Create log
    log_data = schemas.ExecutionLogCreate(
        conversation_id=conversation.id,
        event_type=schemas.EventType.MESSAGE,
        level=schemas.LogLevel.INFO,
        agent_name="Test Agent",
        content="Test log message",
        data={"tokens": 100, "execution_time": 1.5},
    )

    result = log_service.create_log(db_session, log_data)

    assert result.id is not None
    assert result.conversation_id == conversation.id
    assert result.event_type == "message"
    assert result.level == "info"
    assert result.agent_name == "Test Agent"
    assert result.content == "Test log message"
    assert result.data == {"tokens": 100, "execution_time": 1.5}
    assert result.timestamp is not None


def test_get_logs(db_session):
    """Test retrieving logs for a conversation."""
    # Setup
    agent = models.Agent(name="Test Agent", type="assistant", status="active")
    db_session.add(agent)
    db_session.flush()

    conversation = models.Conversation(
        agent_id=agent.id, title="Test Conversation", status="active"
    )
    db_session.add(conversation)
    db_session.commit()

    # Create multiple logs
    for i in range(5):
        log_data = schemas.ExecutionLogCreate(
            conversation_id=conversation.id,
            event_type=schemas.EventType.MESSAGE,
            level=schemas.LogLevel.INFO if i < 3 else schemas.LogLevel.ERROR,
            agent_name="Test Agent",
            content=f"Log message {i}",
        )
        log_service.create_log(db_session, log_data)

    # Test without filter
    logs = log_service.get_logs(db_session, conversation.id)
    assert len(logs) == 5

    # Test with level filter
    filter_params = schemas.LogFilter(level=schemas.LogLevel.ERROR)
    logs = log_service.get_logs(db_session, conversation.id, filter_params)
    assert len(logs) == 2
    assert all(log.level == "error" for log in logs)

    # Test with limit
    filter_params = schemas.LogFilter(limit=2)
    logs = log_service.get_logs(db_session, conversation.id, filter_params)
    assert len(logs) == 2


def test_get_log_stats(db_session):
    """Test getting log statistics."""
    # Setup
    agent = models.Agent(name="Test Agent", type="assistant", status="active")
    db_session.add(agent)
    db_session.flush()

    conversation = models.Conversation(
        agent_id=agent.id, title="Test Conversation", status="active"
    )
    db_session.add(conversation)
    db_session.commit()

    # Create logs with different levels and event types
    log_data = [
        (schemas.EventType.MESSAGE, schemas.LogLevel.INFO),
        (schemas.EventType.MESSAGE, schemas.LogLevel.INFO),
        (schemas.EventType.ERROR, schemas.LogLevel.ERROR),
        (schemas.EventType.FUNCTION_CALL, schemas.LogLevel.DEBUG),
    ]

    for event_type, level in log_data:
        log = schemas.ExecutionLogCreate(
            conversation_id=conversation.id,
            event_type=event_type,
            level=level,
            agent_name="Test Agent",
            content=f"{event_type.value} - {level.value}",
        )
        log_service.create_log(db_session, log)

    # Get stats
    stats = log_service.get_log_stats(db_session, conversation.id)

    assert stats.total_logs == 4
    assert stats.by_level["info"] == 2
    assert stats.by_level["error"] == 1
    assert stats.by_level["debug"] == 1
    assert stats.by_event_type["message"] == 2
    assert stats.by_event_type["error"] == 1
    assert stats.by_event_type["function_call"] == 1
    assert stats.time_range["start"] is not None
    assert stats.time_range["end"] is not None


def test_delete_logs(db_session):
    """Test deleting logs."""
    # Setup
    agent = models.Agent(name="Test Agent", type="assistant", status="active")
    db_session.add(agent)
    db_session.flush()

    conversation = models.Conversation(
        agent_id=agent.id, title="Test Conversation", status="active"
    )
    db_session.add(conversation)
    db_session.commit()

    # Create logs
    for i in range(3):
        log_data = schemas.ExecutionLogCreate(
            conversation_id=conversation.id,
            event_type=schemas.EventType.MESSAGE,
            level=schemas.LogLevel.INFO,
            agent_name="Test Agent",
            content=f"Log message {i}",
        )
        log_service.create_log(db_session, log_data)

    # Delete logs
    count = log_service.delete_logs(db_session, conversation.id)
    assert count == 3

    # Verify deletion
    logs = log_service.get_logs(db_session, conversation.id)
    assert len(logs) == 0


def test_export_logs_json(db_session):
    """Test exporting logs to JSON."""
    # Setup
    agent = models.Agent(name="Test Agent", type="assistant", status="active")
    db_session.add(agent)
    db_session.flush()

    conversation = models.Conversation(
        agent_id=agent.id, title="Test Conversation", status="active"
    )
    db_session.add(conversation)
    db_session.commit()

    # Create logs
    log_data = schemas.ExecutionLogCreate(
        conversation_id=conversation.id,
        event_type=schemas.EventType.MESSAGE,
        level=schemas.LogLevel.INFO,
        agent_name="Test Agent",
        content="Test log message",
        data={"tokens": 100},
    )
    log_service.create_log(db_session, log_data)

    # Export to JSON
    export_data = log_service.export_logs(
        db_session, conversation.id, schemas.LogExportFormat.JSON
    )

    # Verify JSON format
    logs_list = json.loads(export_data)
    assert isinstance(logs_list, list)
    assert len(logs_list) == 1
    assert logs_list[0]["content"] == "Test log message"
    assert logs_list[0]["data"]["tokens"] == 100


def test_export_logs_txt(db_session):
    """Test exporting logs to plain text."""
    # Setup
    agent = models.Agent(name="Test Agent", type="assistant", status="active")
    db_session.add(agent)
    db_session.flush()

    conversation = models.Conversation(
        agent_id=agent.id, title="Test Conversation", status="active"
    )
    db_session.add(conversation)
    db_session.commit()

    # Create log
    log_data = schemas.ExecutionLogCreate(
        conversation_id=conversation.id,
        event_type=schemas.EventType.MESSAGE,
        level=schemas.LogLevel.INFO,
        agent_name="Test Agent",
        content="Test log message",
    )
    log_service.create_log(db_session, log_data)

    # Export to TXT
    export_data = log_service.export_logs(
        db_session, conversation.id, schemas.LogExportFormat.TXT
    )

    # Verify text format
    assert "Test log message" in export_data
    assert "[INFO]" in export_data
    assert "[message]" in export_data
    assert "[Test Agent]" in export_data


def test_export_logs_csv(db_session):
    """Test exporting logs to CSV."""
    # Setup
    agent = models.Agent(name="Test Agent", type="assistant", status="active")
    db_session.add(agent)
    db_session.flush()

    conversation = models.Conversation(
        agent_id=agent.id, title="Test Conversation", status="active"
    )
    db_session.add(conversation)
    db_session.commit()

    # Create log
    log_data = schemas.ExecutionLogCreate(
        conversation_id=conversation.id,
        event_type=schemas.EventType.MESSAGE,
        level=schemas.LogLevel.INFO,
        agent_name="Test Agent",
        content="Test log message",
    )
    log_service.create_log(db_session, log_data)

    # Export to CSV
    export_data = log_service.export_logs(
        db_session, conversation.id, schemas.LogExportFormat.CSV
    )

    # Verify CSV format
    lines = export_data.strip().split("\n")
    assert len(lines) >= 2  # Header + at least one data row
    assert "Timestamp,Level,Event Type,Agent Name,Content,Data" in lines[0]
    assert "info" in lines[1]
    assert "message" in lines[1]
    assert "Test Agent" in lines[1]
    assert "Test log message" in lines[1]
