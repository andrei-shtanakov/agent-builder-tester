"""Analytics service for tracking and aggregating metrics."""

from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from backend.app.models.analytics import (
    AggregatedMetric,
    MetricEvent,
    PerformanceMetric,
    UsageQuota,
)
from backend.app.schemas.analytics import (
    CostBreakdown,
    MetricEventCreate,
    MetricsQuery,
    MetricsSummary,
    PerformanceMetricCreate,
    PerformanceStatistics,
    UsageStatistics,
)


class AnalyticsService:
    """Service for managing analytics and metrics."""

    def __init__(self, db: Session):
        self.db = db

    def create_metric_event(self, metric: MetricEventCreate) -> MetricEvent:
        """Create a new metric event."""
        db_metric = MetricEvent(**metric.model_dump(exclude_unset=True))
        self.db.add(db_metric)
        self.db.commit()
        self.db.refresh(db_metric)
        return db_metric

    def create_performance_metric(
        self, metric: PerformanceMetricCreate
    ) -> PerformanceMetric:
        """Create a new performance metric."""
        db_metric = PerformanceMetric(**metric.model_dump(exclude_unset=True))
        self.db.add(db_metric)
        self.db.commit()
        self.db.refresh(db_metric)
        return db_metric

    def get_metric_events(self, query: MetricsQuery) -> list[MetricEvent]:
        """Query metric events with filters."""
        stmt = select(MetricEvent)

        # Apply filters
        if query.user_id:
            stmt = stmt.where(MetricEvent.user_id == query.user_id)
        if query.agent_id:
            stmt = stmt.where(MetricEvent.agent_id == query.agent_id)
        if query.conversation_id:
            stmt = stmt.where(MetricEvent.conversation_id == query.conversation_id)
        if query.metric_type:
            stmt = stmt.where(MetricEvent.metric_type == query.metric_type)
        if query.metric_name:
            stmt = stmt.where(MetricEvent.metric_name == query.metric_name)
        if query.start_date:
            stmt = stmt.where(MetricEvent.timestamp >= query.start_date)
        if query.end_date:
            stmt = stmt.where(MetricEvent.timestamp <= query.end_date)

        # Apply pagination
        stmt = stmt.order_by(MetricEvent.timestamp.desc())
        stmt = stmt.offset(query.offset).limit(query.limit)

        result = self.db.execute(stmt)
        return list(result.scalars().all())

    def get_metrics_summary(self, query: MetricsQuery) -> MetricsSummary:
        """Get aggregated summary of metrics."""
        stmt = select(
            func.count(MetricEvent.id).label("total_events"),
            func.sum(MetricEvent.value).label("total_value"),
            func.avg(MetricEvent.value).label("average_value"),
            func.min(MetricEvent.value).label("min_value"),
            func.max(MetricEvent.value).label("max_value"),
            MetricEvent.unit,
        )

        # Apply filters
        if query.user_id:
            stmt = stmt.where(MetricEvent.user_id == query.user_id)
        if query.agent_id:
            stmt = stmt.where(MetricEvent.agent_id == query.agent_id)
        if query.conversation_id:
            stmt = stmt.where(MetricEvent.conversation_id == query.conversation_id)
        if query.metric_type:
            stmt = stmt.where(MetricEvent.metric_type == query.metric_type)
        if query.metric_name:
            stmt = stmt.where(MetricEvent.metric_name == query.metric_name)
        if query.start_date:
            stmt = stmt.where(MetricEvent.timestamp >= query.start_date)
        if query.end_date:
            stmt = stmt.where(MetricEvent.timestamp <= query.end_date)

        stmt = stmt.group_by(MetricEvent.unit)

        result = self.db.execute(stmt).first()

        if not result:
            return MetricsSummary(
                total_events=0,
                total_value=0.0,
                average_value=0.0,
                min_value=0.0,
                max_value=0.0,
                unit=None,
                start_date=query.start_date or datetime.now(timezone.utc),
                end_date=query.end_date or datetime.now(timezone.utc),
            )

        return MetricsSummary(
            total_events=result.total_events or 0,
            total_value=result.total_value or 0.0,
            average_value=result.average_value or 0.0,
            min_value=result.min_value or 0.0,
            max_value=result.max_value or 0.0,
            unit=result.unit,
            start_date=query.start_date or datetime.now(timezone.utc),
            end_date=query.end_date or datetime.now(timezone.utc),
        )

    def aggregate_metrics(
        self,
        period: str,
        start_date: datetime,
        end_date: datetime,
        user_id: UUID | None = None,
        agent_id: UUID | None = None,
    ) -> list[AggregatedMetric]:
        """Aggregate metrics for a specific period."""
        # Query raw metrics
        stmt = select(
            MetricEvent.user_id,
            MetricEvent.agent_id,
            MetricEvent.metric_type,
            MetricEvent.metric_name,
            MetricEvent.unit,
            func.count(MetricEvent.id).label("count"),
            func.sum(MetricEvent.value).label("sum"),
            func.avg(MetricEvent.value).label("avg"),
            func.min(MetricEvent.value).label("min"),
            func.max(MetricEvent.value).label("max"),
        ).where(
            and_(
                MetricEvent.timestamp >= start_date, MetricEvent.timestamp < end_date
            )
        )

        if user_id:
            stmt = stmt.where(MetricEvent.user_id == user_id)
        if agent_id:
            stmt = stmt.where(MetricEvent.agent_id == agent_id)

        stmt = stmt.group_by(
            MetricEvent.user_id,
            MetricEvent.agent_id,
            MetricEvent.metric_type,
            MetricEvent.metric_name,
            MetricEvent.unit,
        )

        results = self.db.execute(stmt).all()

        aggregated = []
        for row in results:
            agg_metric = AggregatedMetric(
                user_id=row.user_id,
                agent_id=row.agent_id,
                metric_type=row.metric_type,
                metric_name=row.metric_name,
                aggregation_period=period,
                period_start=start_date,
                period_end=end_date,
                count=row.count,
                sum=row.sum,
                avg=row.avg,
                min=row.min,
                max=row.max,
                unit=row.unit,
            )
            self.db.add(agg_metric)
            aggregated.append(agg_metric)

        self.db.commit()
        return aggregated

    def get_usage_statistics(
        self, user_id: UUID, start_date: datetime, end_date: datetime
    ) -> UsageStatistics:
        """Get comprehensive usage statistics for a user."""
        # Get API call count
        api_calls_stmt = (
            select(func.count(MetricEvent.id))
            .where(
                and_(
                    MetricEvent.user_id == user_id,
                    MetricEvent.metric_type == "api_call",
                    MetricEvent.timestamp >= start_date,
                    MetricEvent.timestamp < end_date,
                )
            )
        )
        total_api_calls = self.db.execute(api_calls_stmt).scalar() or 0

        # Get total tokens
        tokens_stmt = (
            select(func.sum(MetricEvent.value))
            .where(
                and_(
                    MetricEvent.user_id == user_id,
                    MetricEvent.metric_type == "token_usage",
                    MetricEvent.timestamp >= start_date,
                    MetricEvent.timestamp < end_date,
                )
            )
        )
        total_tokens = self.db.execute(tokens_stmt).scalar() or 0

        # Get total cost
        cost_stmt = (
            select(func.sum(MetricEvent.value))
            .where(
                and_(
                    MetricEvent.user_id == user_id,
                    MetricEvent.metric_type == "cost",
                    MetricEvent.timestamp >= start_date,
                    MetricEvent.timestamp < end_date,
                )
            )
        )
        total_cost = self.db.execute(cost_stmt).scalar() or 0.0

        # Get average response time
        latency_stmt = (
            select(func.avg(PerformanceMetric.duration_ms))
            .where(
                and_(
                    PerformanceMetric.timestamp >= start_date,
                    PerformanceMetric.timestamp < end_date,
                )
            )
        )
        avg_response_time = self.db.execute(latency_stmt).scalar() or 0.0

        # Get error rate
        error_stmt = (
            select(
                func.count(PerformanceMetric.id).filter(
                    PerformanceMetric.status == "error"
                )
            )
            .where(
                and_(
                    PerformanceMetric.timestamp >= start_date,
                    PerformanceMetric.timestamp < end_date,
                )
            )
        )
        error_count = self.db.execute(error_stmt).scalar() or 0
        total_requests = (
            self.db.execute(
                select(func.count(PerformanceMetric.id)).where(
                    and_(
                        PerformanceMetric.timestamp >= start_date,
                        PerformanceMetric.timestamp < end_date,
                    )
                )
            ).scalar()
            or 0
        )
        error_rate = error_count / total_requests if total_requests > 0 else 0.0

        # Get quotas
        quotas_stmt = select(UsageQuota).where(UsageQuota.user_id == user_id)
        quotas = list(self.db.execute(quotas_stmt).scalars().all())

        return UsageStatistics(
            user_id=user_id,
            total_api_calls=total_api_calls,
            total_tokens=int(total_tokens),
            total_cost=float(total_cost),
            avg_response_time_ms=float(avg_response_time),
            error_rate=float(error_rate),
            period_start=start_date,
            period_end=end_date,
            quotas=quotas,
        )

    def get_performance_statistics(
        self, operation: str, start_date: datetime, end_date: datetime
    ) -> PerformanceStatistics:
        """Get performance statistics for an operation."""
        stmt = select(
            func.count(PerformanceMetric.id).label("total_calls"),
            func.count(PerformanceMetric.id)
            .filter(PerformanceMetric.status == "success")
            .label("success_count"),
            func.count(PerformanceMetric.id)
            .filter(PerformanceMetric.status == "error")
            .label("error_count"),
            func.avg(PerformanceMetric.duration_ms).label("avg_duration"),
            func.min(PerformanceMetric.duration_ms).label("min_duration"),
            func.max(PerformanceMetric.duration_ms).label("max_duration"),
        ).where(
            and_(
                PerformanceMetric.operation == operation,
                PerformanceMetric.timestamp >= start_date,
                PerformanceMetric.timestamp < end_date,
            )
        )

        result = self.db.execute(stmt).first()

        if not result or result.total_calls == 0:
            return PerformanceStatistics(
                operation=operation,
                total_calls=0,
                success_count=0,
                error_count=0,
                avg_duration_ms=0.0,
                min_duration_ms=0.0,
                max_duration_ms=0.0,
                period_start=start_date,
                period_end=end_date,
            )

        return PerformanceStatistics(
            operation=operation,
            total_calls=result.total_calls,
            success_count=result.success_count,
            error_count=result.error_count,
            avg_duration_ms=result.avg_duration,
            min_duration_ms=result.min_duration,
            max_duration_ms=result.max_duration,
            period_start=start_date,
            period_end=end_date,
        )

    def get_cost_breakdown(
        self, entity_type: str, entity_id: UUID, start_date: datetime, end_date: datetime
    ) -> CostBreakdown:
        """Get cost breakdown for an agent or conversation."""
        filter_col = (
            MetricEvent.agent_id
            if entity_type == "agent"
            else MetricEvent.conversation_id
        )

        # Get total cost
        cost_stmt = (
            select(func.sum(MetricEvent.value))
            .where(
                and_(
                    filter_col == entity_id,
                    MetricEvent.metric_type == "cost",
                    MetricEvent.timestamp >= start_date,
                    MetricEvent.timestamp < end_date,
                )
            )
        )
        total_cost = self.db.execute(cost_stmt).scalar() or 0.0

        # Get total tokens
        tokens_stmt = (
            select(func.sum(MetricEvent.value))
            .where(
                and_(
                    filter_col == entity_id,
                    MetricEvent.metric_type == "token_usage",
                    MetricEvent.timestamp >= start_date,
                    MetricEvent.timestamp < end_date,
                )
            )
        )
        total_tokens = self.db.execute(tokens_stmt).scalar() or 0

        # Get API calls
        api_calls_stmt = (
            select(func.count(MetricEvent.id))
            .where(
                and_(
                    filter_col == entity_id,
                    MetricEvent.metric_type == "api_call",
                    MetricEvent.timestamp >= start_date,
                    MetricEvent.timestamp < end_date,
                )
            )
        )
        api_calls = self.db.execute(api_calls_stmt).scalar() or 0

        return CostBreakdown(
            entity_id=entity_id,
            entity_type=entity_type,
            total_cost=float(total_cost),
            total_tokens=int(total_tokens),
            api_calls=api_calls,
            period_start=start_date,
            period_end=end_date,
        )

    def update_usage_quota(
        self, user_id: UUID, quota_type: str, increment: float
    ) -> UsageQuota | None:
        """Update a user's usage quota."""
        stmt = select(UsageQuota).where(
            and_(UsageQuota.user_id == user_id, UsageQuota.quota_type == quota_type)
        )
        quota = self.db.execute(stmt).scalar_one_or_none()

        if not quota:
            return None

        # Check if quota needs reset
        now = datetime.now(timezone.utc)
        if now >= quota.next_reset:
            quota.used = 0.0
            quota.last_reset = now
            quota.next_reset = self._calculate_next_reset(now, quota.reset_period)

        # Increment usage
        quota.used += increment
        self.db.commit()
        self.db.refresh(quota)
        return quota

    def _calculate_next_reset(self, current_time: datetime, period: str) -> datetime:
        """Calculate the next reset time based on the period."""
        if period == "hour":
            return current_time + timedelta(hours=1)
        elif period == "day":
            return current_time + timedelta(days=1)
        elif period == "week":
            return current_time + timedelta(weeks=1)
        elif period == "month":
            return current_time + timedelta(days=30)
        return current_time + timedelta(days=1)

    def check_quota_exceeded(
        self, user_id: UUID, quota_type: str
    ) -> tuple[bool, UsageQuota | None]:
        """Check if a user has exceeded their quota."""
        stmt = select(UsageQuota).where(
            and_(UsageQuota.user_id == user_id, UsageQuota.quota_type == quota_type)
        )
        quota = self.db.execute(stmt).scalar_one_or_none()

        if not quota:
            return False, None

        exceeded = quota.used >= quota.limit
        return exceeded, quota
