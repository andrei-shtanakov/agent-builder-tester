"""Analytics API endpoints."""

from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from backend.app import schemas
from backend.app.core.dependencies import get_current_active_user
from backend.app.database import get_db
from backend.app.middleware.rate_limit import limiter
from backend.app.models.user import User
from backend.app.services.analytics_service import AnalyticsService

router = APIRouter()


def get_analytics_service(db: Session = Depends(get_db)) -> AnalyticsService:
    """Get analytics service instance."""
    return AnalyticsService(db)


@router.post(
    "/metrics",
    response_model=schemas.MetricEventResponse,
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit("100/minute")
def create_metric_event(
    request: Request,
    metric: schemas.MetricEventCreate,
    current_user: User = Depends(get_current_active_user),
    analytics: AnalyticsService = Depends(get_analytics_service),
) -> schemas.MetricEventResponse:
    """
    Create a new metric event.

    Track usage metrics like API calls, token usage, costs, etc.
    """
    # Ensure user_id is set to current user if not provided
    if not metric.user_id:
        metric.user_id = current_user.id

    db_metric = analytics.create_metric_event(metric)
    return schemas.MetricEventResponse.model_validate(db_metric)


@router.post(
    "/performance",
    response_model=schemas.PerformanceMetricResponse,
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit("100/minute")
def create_performance_metric(
    request: Request,
    metric: schemas.PerformanceMetricCreate,
    current_user: User = Depends(get_current_active_user),
    analytics: AnalyticsService = Depends(get_analytics_service),
) -> schemas.PerformanceMetricResponse:
    """
    Create a new performance metric.

    Track operation performance, latency, and errors.
    """
    db_metric = analytics.create_performance_metric(metric)
    return schemas.PerformanceMetricResponse.model_validate(db_metric)


@router.get("/metrics", response_model=list[schemas.MetricEventResponse])
@limiter.limit("60/minute")
def get_metrics(
    request: Request,
    user_id: UUID | None = None,
    agent_id: UUID | None = None,
    conversation_id: UUID | None = None,
    metric_type: str | None = None,
    metric_name: str | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_active_user),
    analytics: AnalyticsService = Depends(get_analytics_service),
) -> list[schemas.MetricEventResponse]:
    """
    Query metric events with filters.

    Returns paginated list of metric events matching the criteria.
    """
    query = schemas.MetricsQuery(
        user_id=user_id,
        agent_id=agent_id,
        conversation_id=conversation_id,
        metric_type=metric_type,
        metric_name=metric_name,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset,
    )

    # Non-superusers can only query their own metrics
    if not current_user.is_superuser:
        query.user_id = current_user.id

    metrics = analytics.get_metric_events(query)
    return [schemas.MetricEventResponse.model_validate(m) for m in metrics]


@router.get("/metrics/summary", response_model=schemas.MetricsSummary)
@limiter.limit("60/minute")
def get_metrics_summary(
    request: Request,
    user_id: UUID | None = None,
    agent_id: UUID | None = None,
    conversation_id: UUID | None = None,
    metric_type: str | None = None,
    metric_name: str | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    current_user: User = Depends(get_current_active_user),
    analytics: AnalyticsService = Depends(get_analytics_service),
) -> schemas.MetricsSummary:
    """
    Get aggregated summary of metrics.

    Returns statistical summary (count, sum, avg, min, max) for matching metrics.
    """
    query = schemas.MetricsQuery(
        user_id=user_id,
        agent_id=agent_id,
        conversation_id=conversation_id,
        metric_type=metric_type,
        metric_name=metric_name,
        start_date=start_date,
        end_date=end_date,
    )

    # Non-superusers can only query their own metrics
    if not current_user.is_superuser:
        query.user_id = current_user.id

    return analytics.get_metrics_summary(query)


@router.get("/usage/statistics", response_model=schemas.UsageStatistics)
@limiter.limit("60/minute")
def get_usage_statistics(
    request: Request,
    user_id: UUID | None = None,
    start_date: datetime | None = Query(None),
    end_date: datetime | None = Query(None),
    current_user: User = Depends(get_current_active_user),
    analytics: AnalyticsService = Depends(get_analytics_service),
) -> schemas.UsageStatistics:
    """
    Get comprehensive usage statistics for a user.

    Includes API calls, tokens, costs, response times, and error rates.
    Non-superusers can only view their own statistics.
    """
    # Default to last 30 days if no dates provided
    if not end_date:
        end_date = datetime.now(timezone.utc)
    if not start_date:
        start_date = end_date.replace(day=1)  # Start of current month

    # Non-superusers can only query their own stats
    target_user_id = user_id if user_id else current_user.id
    if not current_user.is_superuser and target_user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot view other users' statistics",
        )

    return analytics.get_usage_statistics(target_user_id, start_date, end_date)


@router.get(
    "/performance/statistics", response_model=schemas.PerformanceStatistics
)
@limiter.limit("60/minute")
def get_performance_statistics(
    request: Request,
    operation: str = Query(..., description="Operation or endpoint name"),
    start_date: datetime | None = Query(None),
    end_date: datetime | None = Query(None),
    current_user: User = Depends(get_current_active_user),
    analytics: AnalyticsService = Depends(get_analytics_service),
) -> schemas.PerformanceStatistics:
    """
    Get performance statistics for a specific operation.

    Returns success/error counts, latency percentiles, and timing statistics.
    """
    # Default to last 24 hours if no dates provided
    if not end_date:
        end_date = datetime.now(timezone.utc)
    if not start_date:
        start_date = end_date.replace(
            hour=0, minute=0, second=0, microsecond=0
        )  # Start of day

    return analytics.get_performance_statistics(operation, start_date, end_date)


@router.get("/costs/breakdown", response_model=schemas.CostBreakdown)
@limiter.limit("60/minute")
def get_cost_breakdown(
    request: Request,
    entity_type: str = Query(..., description="Entity type: agent or conversation"),
    entity_id: UUID = Query(..., description="Entity ID"),
    start_date: datetime | None = Query(None),
    end_date: datetime | None = Query(None),
    current_user: User = Depends(get_current_active_user),
    analytics: AnalyticsService = Depends(get_analytics_service),
) -> schemas.CostBreakdown:
    """
    Get cost breakdown for an agent or conversation.

    Returns total costs, token usage, and API call counts.
    """
    if entity_type not in ["agent", "conversation"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="entity_type must be 'agent' or 'conversation'",
        )

    # Default to last 30 days if no dates provided
    if not end_date:
        end_date = datetime.now(timezone.utc)
    if not start_date:
        start_date = end_date.replace(day=1)  # Start of current month

    return analytics.get_cost_breakdown(entity_type, entity_id, start_date, end_date)


@router.get("/quotas/me", response_model=list[schemas.UsageQuotaResponse])
@limiter.limit("60/minute")
def get_my_quotas(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> list[schemas.UsageQuotaResponse]:
    """
    Get current user's usage quotas.

    Returns all quota limits and current usage for the authenticated user.
    """
    from backend.app.models.analytics import UsageQuota
    from sqlalchemy import select

    stmt = select(UsageQuota).where(UsageQuota.user_id == current_user.id)
    quotas = list(db.execute(stmt).scalars().all())
    return [schemas.UsageQuotaResponse.model_validate(q) for q in quotas]


@router.get("/quotas/check/{quota_type}")
@limiter.limit("100/minute")
def check_quota(
    request: Request,
    quota_type: str,
    current_user: User = Depends(get_current_active_user),
    analytics: AnalyticsService = Depends(get_analytics_service),
) -> dict:
    """
    Check if user has exceeded a specific quota.

    Returns quota status and remaining allowance.
    """
    exceeded, quota = analytics.check_quota_exceeded(current_user.id, quota_type)

    if not quota:
        return {
            "quota_type": quota_type,
            "exists": False,
            "exceeded": False,
            "message": "No quota configured for this type",
        }

    remaining = max(0.0, quota.limit - quota.used)
    percentage = (quota.used / quota.limit * 100.0) if quota.limit > 0 else 0.0

    return {
        "quota_type": quota_type,
        "exists": True,
        "exceeded": exceeded,
        "limit": quota.limit,
        "used": quota.used,
        "remaining": remaining,
        "percentage": percentage,
        "reset_period": quota.reset_period,
        "next_reset": quota.next_reset,
    }
