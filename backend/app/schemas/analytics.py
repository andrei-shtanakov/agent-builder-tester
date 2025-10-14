"""Analytics API schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class MetricEventCreate(BaseModel):
    """Schema for creating a metric event."""

    model_config = ConfigDict(populate_by_name=True)

    user_id: UUID | None = None
    agent_id: UUID | None = None
    conversation_id: UUID | None = None
    metric_type: str = Field(..., description="Type of metric (e.g., api_call, cost)")
    metric_name: str = Field(..., description="Specific metric name")
    value: float = Field(..., description="Numeric value of the metric")
    unit: str | None = Field(None, description="Unit of measurement (e.g., tokens, ms)")
    extra_metadata: dict | None = Field(
        None,
        validation_alias=AliasChoices("metadata", "extra_metadata"),
        serialization_alias="metadata",
        description="Additional context",
    )


class MetricEventResponse(BaseModel):
    """Schema for metric event response."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: UUID
    user_id: UUID | None
    agent_id: UUID | None
    conversation_id: UUID | None
    metric_type: str
    metric_name: str
    value: float
    unit: str | None
    extra_metadata: dict | None = Field(None, serialization_alias="metadata")
    timestamp: datetime


class AggregatedMetricResponse(BaseModel):
    """Schema for aggregated metric response."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: UUID
    user_id: UUID | None
    agent_id: UUID | None
    metric_type: str
    metric_name: str
    aggregation_period: str
    period_start: datetime
    period_end: datetime
    count: int
    sum: float
    avg: float
    min: float
    max: float
    unit: str | None
    extra_metadata: dict | None = Field(None, serialization_alias="metadata")
    created_at: datetime
    updated_at: datetime


class UsageQuotaResponse(BaseModel):
    """Schema for usage quota response."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: UUID
    user_id: UUID
    quota_type: str
    limit: float
    used: float
    reset_period: str
    last_reset: datetime
    next_reset: datetime
    extra_metadata: dict | None = Field(None, serialization_alias="metadata")
    created_at: datetime
    updated_at: datetime


class PerformanceMetricCreate(BaseModel):
    """Schema for creating a performance metric."""

    model_config = ConfigDict(populate_by_name=True)

    agent_id: UUID | None = None
    conversation_id: UUID | None = None
    operation: str = Field(..., description="Operation or endpoint name")
    duration_ms: float = Field(..., description="Duration in milliseconds")
    status: str = Field(..., description="Status (success, error)")
    error_message: str | None = None
    extra_metadata: dict | None = Field(
        None,
        validation_alias=AliasChoices("metadata", "extra_metadata"),
        serialization_alias="metadata",
    )


class PerformanceMetricResponse(BaseModel):
    """Schema for performance metric response."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: UUID
    agent_id: UUID | None
    conversation_id: UUID | None
    operation: str
    duration_ms: float
    status: str
    error_message: str | None
    extra_metadata: dict | None = Field(None, serialization_alias="metadata")
    timestamp: datetime


class MetricsQuery(BaseModel):
    """Schema for querying metrics."""

    user_id: UUID | None = None
    agent_id: UUID | None = None
    conversation_id: UUID | None = None
    metric_type: str | None = None
    metric_name: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    aggregation_period: str | None = Field(
        None, description="Period for aggregation (hour, day, week, month)"
    )
    limit: int = Field(100, ge=1, le=1000)
    offset: int = Field(0, ge=0)


class MetricsSummary(BaseModel):
    """Schema for metrics summary response."""

    total_events: int
    total_value: float
    average_value: float
    min_value: float
    max_value: float
    unit: str | None
    start_date: datetime
    end_date: datetime


class UsageStatistics(BaseModel):
    """Schema for user usage statistics."""

    model_config = ConfigDict(populate_by_name=True)

    user_id: UUID
    total_api_calls: int
    total_tokens: int
    total_cost: float
    avg_response_time_ms: float
    error_rate: float
    period_start: datetime
    period_end: datetime
    quotas: list[UsageQuotaResponse] = Field(default_factory=list)


class PerformanceStatistics(BaseModel):
    """Schema for performance statistics."""

    model_config = ConfigDict(populate_by_name=True)

    operation: str
    total_calls: int
    success_count: int
    error_count: int
    avg_duration_ms: float
    min_duration_ms: float
    max_duration_ms: float
    p50_duration_ms: float | None = None
    p95_duration_ms: float | None = None
    p99_duration_ms: float | None = None
    period_start: datetime
    period_end: datetime


class CostBreakdown(BaseModel):
    """Schema for cost breakdown by agent or conversation."""

    model_config = ConfigDict(populate_by_name=True)

    entity_id: UUID
    entity_type: str  # 'agent' or 'conversation'
    total_cost: float
    total_tokens: int
    api_calls: int
    period_start: datetime
    period_end: datetime
    breakdown: dict | None = None  # Detailed breakdown by model/operation
