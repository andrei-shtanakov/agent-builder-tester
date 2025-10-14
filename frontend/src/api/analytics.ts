import { apiFetch } from "./client";
import type {
  CostBreakdown,
  MetricEvent,
  MetricsSummary,
  PerformanceStatistics,
  UsageStatistics,
} from "./types";

export interface MetricsSummaryParams {
  metric_type?: string;
  metric_name?: string;
  agent_id?: string;
  conversation_id?: string;
  start_date?: string;
  end_date?: string;
}

export interface UsageStatisticsParams {
  user_id?: string;
  start_date?: string;
  end_date?: string;
}

export interface PerformanceStatisticsParams {
  operation: string;
  start_date?: string;
  end_date?: string;
}

export interface CostBreakdownParams {
  entity_type: "agent" | "conversation";
  entity_id: string;
  start_date?: string;
  end_date?: string;
}

export interface MetricEventsParams {
  metric_type?: string;
  metric_name?: string;
  agent_id?: string;
  conversation_id?: string;
  start_date?: string;
  end_date?: string;
  limit?: number;
  offset?: number;
}

const buildQueryString = (params: Record<string, string | undefined>) => {
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value) {
      search.set(key, value);
    }
  });
  const query = search.toString();
  return query.length > 0 ? `?${query}` : "";
};

export const fetchMetricsSummary = (
  params: MetricsSummaryParams,
): Promise<MetricsSummary> =>
  apiFetch<MetricsSummary>(`/analytics/metrics/summary${buildQueryString(params)}`);

export const fetchUsageStatistics = (
  params: UsageStatisticsParams,
): Promise<UsageStatistics> =>
  apiFetch<UsageStatistics>(`/analytics/usage/statistics${buildQueryString(params)}`);

export const fetchPerformanceStatistics = (
  params: PerformanceStatisticsParams,
): Promise<PerformanceStatistics> =>
  apiFetch<PerformanceStatistics>(
    `/analytics/performance/statistics${buildQueryString(params)}`,
  );

export const fetchCostBreakdown = (
  params: CostBreakdownParams,
): Promise<CostBreakdown> =>
  apiFetch<CostBreakdown>(`/analytics/costs/breakdown${buildQueryString(params)}`);

export const fetchMetricEvents = (
  params: MetricEventsParams,
): Promise<MetricEvent[]> =>
  apiFetch<MetricEvent[]>(`/analytics/metrics${buildQueryString({
    ...params,
    limit: params.limit?.toString(),
    offset: params.offset?.toString(),
  })}`);
