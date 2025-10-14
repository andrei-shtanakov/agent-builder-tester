import { useEffect, useMemo, useState, type ReactNode } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  fetchCostBreakdown,
  fetchMetricEvents,
  fetchMetricsSummary,
  fetchPerformanceStatistics,
  fetchUsageStatistics,
} from "../api/analytics";
import type {
  CostBreakdown,
  MetricEvent,
  MetricsSummary,
  PerformanceStatistics,
  UsageStatistics,
} from "../api/types";

interface DateRangeState {
  startDate: string;
  endDate: string;
}

const toIso = (dateInput: string, endOfDay: boolean): string => {
  const base = new Date(`${dateInput}T00:00:00Z`);
  if (Number.isNaN(base.getTime())) {
    return new Date().toISOString();
  }
  if (endOfDay) {
    base.setUTCHours(23, 59, 59, 999);
  }
  return base.toISOString();
};

const DEFAULT_OPERATION = "agent.run";

export function AnalyticsDashboardPage(): JSX.Element {
  const [dateRange, setDateRange] = useState<DateRangeState>(() => {
    const now = new Date();
    const endDate = now.toISOString().slice(0, 10);
    const sevenDaysAgo = new Date(now.getTime() - 6 * 24 * 60 * 60 * 1000);
    const startDate = sevenDaysAgo.toISOString().slice(0, 10);
    return { startDate, endDate };
  });

  const [operation, setOperation] = useState<string>(DEFAULT_OPERATION);
  const [costEntityId, setCostEntityId] = useState<string>("");
  const [costEntityType, setCostEntityType] = useState<"agent" | "conversation">(
    "agent",
  );

  const isoRange = useMemo(() => {
    const startIso = toIso(dateRange.startDate, false);
    const endIso = toIso(dateRange.endDate, true);
    return { startIso, endIso };
  }, [dateRange.endDate, dateRange.startDate]);

  const usageStatsQuery = useQuery<UsageStatistics, Error>({
    queryKey: ["usage", isoRange],
    queryFn: () =>
      fetchUsageStatistics({
        start_date: isoRange.startIso,
        end_date: isoRange.endIso,
      }),
    staleTime: 60 * 1000,
  });

  const costSummaryQuery = useQuery<MetricsSummary, Error>({
    queryKey: ["metrics", "cost", isoRange],
    queryFn: () =>
      fetchMetricsSummary({
        metric_type: "cost",
        start_date: isoRange.startIso,
        end_date: isoRange.endIso,
      }),
    staleTime: 60 * 1000,
  });

  const tokenSummaryQuery = useQuery<MetricsSummary, Error>({
    queryKey: ["metrics", "token_usage", isoRange],
    queryFn: () =>
      fetchMetricsSummary({
        metric_type: "token_usage",
        start_date: isoRange.startIso,
        end_date: isoRange.endIso,
      }),
    staleTime: 60 * 1000,
  });

  const apiCallSummaryQuery = useQuery<MetricsSummary, Error>({
    queryKey: ["metrics", "api_call", isoRange],
    queryFn: () =>
      fetchMetricsSummary({
        metric_type: "api_call",
        start_date: isoRange.startIso,
        end_date: isoRange.endIso,
      }),
    staleTime: 60 * 1000,
  });

  const performanceQuery = useQuery<PerformanceStatistics, Error>({
    queryKey: ["performance", operation, isoRange],
    queryFn: () =>
      fetchPerformanceStatistics({
        operation,
        start_date: isoRange.startIso,
        end_date: isoRange.endIso,
      }),
    enabled: operation.trim().length > 0,
    staleTime: 60 * 1000,
  });

  const costBreakdownQuery = useQuery<CostBreakdown, Error>({
    queryKey: ["cost-breakdown", costEntityType, costEntityId, isoRange],
    queryFn: () =>
      fetchCostBreakdown({
        entity_type: costEntityType,
        entity_id: costEntityId,
        start_date: isoRange.startIso,
        end_date: isoRange.endIso,
      }),
    enabled: costEntityId.trim().length > 0,
    staleTime: 60 * 1000,
  });

  const costTrendQuery = useQuery<MetricEvent[], Error>({
    queryKey: ["metric-events", "cost", isoRange],
    queryFn: () =>
      fetchMetricEvents({
        metric_type: "cost",
        start_date: isoRange.startIso,
        end_date: isoRange.endIso,
        limit: 200,
      }),
    select: (events) =>
      [...events].sort(
        (a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime(),
      ),
    staleTime: 60 * 1000,
  });

  const tokensTrendQuery = useQuery<MetricEvent[], Error>({
    queryKey: ["metric-events", "token_usage", isoRange],
    queryFn: () =>
      fetchMetricEvents({
        metric_type: "token_usage",
        start_date: isoRange.startIso,
        end_date: isoRange.endIso,
        limit: 200,
      }),
    select: (events) =>
      [...events].sort(
        (a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime(),
      ),
    staleTime: 60 * 1000,
  });

  const refreshAll = () => {
    void usageStatsQuery.refetch();
    void costSummaryQuery.refetch();
    void tokenSummaryQuery.refetch();
    void apiCallSummaryQuery.refetch();
    if (operation.trim().length > 0) {
      void performanceQuery.refetch();
    }
    if (costEntityId.trim().length > 0) {
      void costBreakdownQuery.refetch();
    }
  };

  useEffect(() => {
    if (!operation) {
      setOperation(DEFAULT_OPERATION);
    }
  }, [operation]);

  const formatNumber = (value: number, fractionDigits = 2): string =>
    new Intl.NumberFormat(undefined, {
      minimumFractionDigits: fractionDigits,
      maximumFractionDigits: fractionDigits,
    }).format(value);

  const formatPercent = (value: number): string =>
    `${formatNumber(value * 100, 2)}%`;

  const resolveCost = (): number | null => {
    if (costSummaryQuery.data) {
      return costSummaryQuery.data.total_value;
    }
    if (usageStatsQuery.data) {
      return usageStatsQuery.data.total_cost;
    }
    return null;
  };

  return (
    <div className="page page--analytics-dashboard">
      <header className="page__header">
        <div>
          <h1>Analytics &amp; Metrics Dashboard</h1>
          <p>
            Track usage, costs, and performance for your agents. Adjust the date range
            or focus on a specific operation to see real-time trends.
          </p>
        </div>
        <button className="button button--secondary" type="button" onClick={refreshAll}>
          Refresh
        </button>
      </header>

      <section className="page__section analytics-controls">
        <div className="form-field">
          <span className="form-label">Start Date</span>
          <input
            className="form-input"
            type="date"
            value={dateRange.startDate}
            max={dateRange.endDate}
            onChange={(event) =>
              setDateRange((prev) => ({ ...prev, startDate: event.target.value }))
            }
          />
        </div>
        <div className="form-field">
          <span className="form-label">End Date</span>
          <input
            className="form-input"
            type="date"
            value={dateRange.endDate}
            min={dateRange.startDate}
            onChange={(event) =>
              setDateRange((prev) => ({ ...prev, endDate: event.target.value }))
            }
          />
        </div>
        <div className="form-field">
          <span className="form-label">Operation</span>
          <input
            className="form-input"
            type="text"
            value={operation}
            onChange={(event) => setOperation(event.target.value)}
            placeholder="Enter operation identifier"
          />
        </div>
        <div className="form-field">
          <span className="form-label">Cost Entity</span>
          <div className="analytics-cost-control">
            <select
              className="form-select"
              value={costEntityType}
              onChange={(event) =>
                setCostEntityType(event.target.value as "agent" | "conversation")
              }
            >
              <option value="agent">Agent</option>
              <option value="conversation">Conversation</option>
            </select>
            <input
              className="form-input analytics-cost-control__input"
              type="text"
              value={costEntityId}
              onChange={(event) => setCostEntityId(event.target.value)}
              placeholder="UUID"
            />
          </div>
        </div>
      </section>

      <section className="page__section">
        <div className="metrics metrics--analytics">
          <MetricCard
            title="Total Cost"
            value={resolveCost()}
            unit={costSummaryQuery.data?.unit ?? "USD"}
            isLoading={costSummaryQuery.isLoading || usageStatsQuery.isLoading}
            error={costSummaryQuery.error?.message}
          />
          <MetricCard
            title="Total Tokens"
            value={tokenSummaryQuery.data?.total_value ?? usageStatsQuery.data?.total_tokens}
            unit="tokens"
            isLoading={tokenSummaryQuery.isLoading || usageStatsQuery.isLoading}
            error={tokenSummaryQuery.error?.message}
          />
          <MetricCard
            title="API Calls"
            value={apiCallSummaryQuery.data?.total_events ?? usageStatsQuery.data?.total_api_calls}
            unit="calls"
            isLoading={apiCallSummaryQuery.isLoading || usageStatsQuery.isLoading}
            error={apiCallSummaryQuery.error?.message}
          />
          <MetricCard
            title="Error Rate"
            value={usageStatsQuery.data?.error_rate}
            unit=""
            formatter={formatPercent}
            isLoading={usageStatsQuery.isLoading}
            error={usageStatsQuery.error?.message}
          />
        </div>
      </section>

      <section className="page__section">
        <div className="analytics-panels">
          <AnalyticsPanel title="Usage Breakdown">
            <UsageTable
              usage={usageStatsQuery.data}
              isLoading={usageStatsQuery.isLoading}
              error={usageStatsQuery.error?.message}
              formatNumber={formatNumber}
              formatPercent={formatPercent}
            />
          </AnalyticsPanel>
          <AnalyticsPanel title="Performance Metrics">
            <PerformanceTable
              statistics={performanceQuery.data}
              isLoading={performanceQuery.isLoading}
              error={performanceQuery.error?.message}
              formatNumber={formatNumber}
            />
          </AnalyticsPanel>
        </div>
      </section>

      <section className="page__section">
        <div className="analytics-panels">
          <AnalyticsPanel title="Cost Trend">
            <AnalyticsLineChart
              points={buildTrendPoints(costTrendQuery.data)}
              isLoading={costTrendQuery.isLoading}
              error={costTrendQuery.error?.message}
              color="#38bdf8"
              unit={costSummaryQuery.data?.unit ?? "USD"}
              valueFormatter={(value) => `$${formatNumber(value)}`}
            />
          </AnalyticsPanel>
          <AnalyticsPanel title="Token Usage Trend">
            <AnalyticsLineChart
              points={buildTrendPoints(tokensTrendQuery.data)}
              isLoading={tokensTrendQuery.isLoading}
              error={tokensTrendQuery.error?.message}
              color="#a855f7"
              unit="tokens"
              valueFormatter={(value) => formatNumber(value, 0)}
            />
          </AnalyticsPanel>
        </div>
      </section>

      <section className="page__section">
        <AnalyticsPanel title="Cost Breakdown">
          <CostBreakdownTable
            breakdown={costBreakdownQuery.data}
            isLoading={costBreakdownQuery.isLoading}
            error={costBreakdownQuery.error?.message}
            formatNumber={formatNumber}
          />
        </AnalyticsPanel>
      </section>
    </div>
  );
}

interface MetricCardProps {
  title: string;
  value: number | null | undefined;
  unit: string;
  isLoading: boolean;
  error?: string;
  formatter?: (value: number) => string;
}

function MetricCard(props: MetricCardProps): JSX.Element {
  const { title, value, unit, isLoading, error, formatter } = props;

  let display: string | JSX.Element = "—";
  if (error) {
    display = <span className="metrics__error">{error}</span>;
  } else if (isLoading) {
    display = <span className="metrics__loading">Loading…</span>;
  } else if (value !== null && value !== undefined) {
    display = formatter ? formatter(value) : new Intl.NumberFormat().format(value);
  }

  return (
    <div className="metrics__card metrics__card--analytics">
      <span className="metrics__label">{title}</span>
      <span className="metrics__value">{display}</span>
      {unit ? <span className="metrics__unit">{unit}</span> : null}
    </div>
  );
}

interface AnalyticsPanelProps {
  title: string;
  children: ReactNode;
}

function AnalyticsPanel({ title, children }: AnalyticsPanelProps): JSX.Element {
  return (
    <div className="analytics-panel">
      <header className="analytics-panel__header">
        <h2>{title}</h2>
      </header>
      <div className="analytics-panel__body">{children}</div>
    </div>
  );
}

interface UsageTableProps {
  usage: UsageStatistics | undefined;
  isLoading: boolean;
  error: string | undefined;
  formatNumber: (value: number, fractionDigits?: number) => string;
  formatPercent: (value: number) => string;
}

function UsageTable(props: UsageTableProps): JSX.Element {
  const { usage, isLoading, error, formatNumber, formatPercent } = props;

  if (error) {
    return <div className="analytics-panel__placeholder analytics-panel__placeholder--error">{error}</div>;
  }

  if (isLoading || !usage) {
    return <div className="analytics-panel__placeholder">{isLoading ? "Loading usage statistics…" : "No usage data"}</div>;
  }

  return (
    <table className="analytics-table">
      <tbody>
        <tr>
          <th scope="row">API Calls</th>
          <td>{usage.total_api_calls}</td>
        </tr>
        <tr>
          <th scope="row">Tokens Consumed</th>
          <td>{usage.total_tokens}</td>
        </tr>
        <tr>
          <th scope="row">Total Cost</th>
          <td>${formatNumber(usage.total_cost)}</td>
        </tr>
        <tr>
          <th scope="row">Average Latency</th>
          <td>{formatNumber(usage.avg_response_time_ms)} ms</td>
        </tr>
        <tr>
          <th scope="row">Error Rate</th>
          <td>{formatPercent(usage.error_rate)}</td>
        </tr>
      </tbody>
    </table>
  );
}

interface PerformanceTableProps {
  statistics: PerformanceStatistics | undefined;
  isLoading: boolean;
  error: string | undefined;
  formatNumber: (value: number, fractionDigits?: number) => string;
}

function PerformanceTable(props: PerformanceTableProps): JSX.Element {
  const { statistics, isLoading, error, formatNumber } = props;

  if (error) {
    return <div className="analytics-panel__placeholder analytics-panel__placeholder--error">{error}</div>;
  }

  if (isLoading || !statistics) {
    return <div className="analytics-panel__placeholder">{isLoading ? "Loading performance data…" : "No performance data"}</div>;
  }

  return (
    <table className="analytics-table">
      <tbody>
        <tr>
          <th scope="row">Operation</th>
          <td>{statistics.operation}</td>
        </tr>
        <tr>
          <th scope="row">Total Calls</th>
          <td>{statistics.total_calls}</td>
        </tr>
        <tr>
          <th scope="row">Successes</th>
          <td>{statistics.success_count}</td>
        </tr>
        <tr>
          <th scope="row">Errors</th>
          <td>{statistics.error_count}</td>
        </tr>
        <tr>
          <th scope="row">Average Duration</th>
          <td>{formatNumber(statistics.avg_duration_ms)} ms</td>
        </tr>
        <tr>
          <th scope="row">Min / Max Duration</th>
          <td>
            {formatNumber(statistics.min_duration_ms)} ms / {" "}
            {formatNumber(statistics.max_duration_ms)} ms
          </td>
        </tr>
      </tbody>
    </table>
  );
}

interface CostBreakdownTableProps {
  breakdown: CostBreakdown | undefined;
  isLoading: boolean;
  error: string | undefined;
  formatNumber: (value: number, fractionDigits?: number) => string;
}

function CostBreakdownTable(props: CostBreakdownTableProps): JSX.Element {
  const { breakdown, isLoading, error, formatNumber } = props;

  if (error) {
    return <div className="analytics-panel__placeholder analytics-panel__placeholder--error">{error}</div>;
  }

  if (!breakdown) {
    return (
      <div className="analytics-panel__placeholder">
        {isLoading ? "Loading cost breakdown…" : "Provide an entity ID to view costs"}
      </div>
    );
  }

  const rows: Array<[string, ReactNode]> = [
    ["Entity Type", breakdown.entity_type],
    ["Entity ID", breakdown.entity_id],
    ["Total Cost", `$${formatNumber(breakdown.total_cost)}`],
    ["Tokens", formatNumber(breakdown.total_tokens, 0)],
    ["API Calls", formatNumber(breakdown.api_calls, 0)],
  ];

  if (breakdown.breakdown && Object.keys(breakdown.breakdown).length > 0) {
    rows.push([
      "Breakdown",
      <pre className="analytics-table__pre" key="breakdown-pre">
        {JSON.stringify(breakdown.breakdown, null, 2)}
      </pre>,
    ]);
  }

  return (
    <table className="analytics-table">
      <tbody>
        {rows.map(([label, value]) => (
          <tr key={label}>
            <th scope="row">{label}</th>
            <td className="analytics-table__value analytics-table__value--wrap">{value}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

interface TrendDatum {
  timestamp: number;
  iso: string;
  value: number;
}

const buildTrendPoints = (events: MetricEvent[] | undefined): TrendDatum[] => {
  if (!events || events.length === 0) {
    return [];
  }

  return events.map((event) => ({
    timestamp: new Date(event.timestamp).getTime(),
    iso: event.timestamp,
    value: event.value,
  }));
};

interface AnalyticsLineChartProps {
  points: TrendDatum[];
  isLoading: boolean;
  error?: string;
  color: string;
  unit: string;
  valueFormatter?: (value: number) => string;
}

function AnalyticsLineChart(props: AnalyticsLineChartProps): JSX.Element {
  const { points, isLoading, error, color, unit, valueFormatter } = props;

  if (error) {
    return (
      <div className="analytics-panel__placeholder analytics-panel__placeholder--error">
        {error}
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="analytics-panel__placeholder">Loading trend data…</div>
    );
  }

  if (!points.length) {
    return (
      <div className="analytics-panel__placeholder">
        No data in the selected range.
      </div>
    );
  }

  const chartWidth = 540;
  const chartHeight = 240;
  const margin = { top: 16, right: 24, bottom: 32, left: 48 };
  const innerWidth = chartWidth - margin.left - margin.right;
  const innerHeight = chartHeight - margin.top - margin.bottom;

  const minTimestamp = Math.min(...points.map((point) => point.timestamp));
  const maxTimestamp = Math.max(...points.map((point) => point.timestamp));
  const minValue = Math.min(...points.map((point) => point.value));
  const maxValue = Math.max(...points.map((point) => point.value));
  const valueRange = maxValue - minValue || 1;
  const timeRange = maxTimestamp - minTimestamp || 1;

  const mapX = (timestamp: number): number =>
    margin.left + ((timestamp - minTimestamp) / timeRange) * innerWidth;
  const mapY = (value: number): number =>
    margin.top + (1 - (value - minValue) / valueRange) * innerHeight;

  const path = points
    .map((point, index) => {
      const command = index === 0 ? "M" : "L";
      return `${command}${mapX(point.timestamp)} ${mapY(point.value)}`;
    })
    .join(" ");

  const ticks = 5;
  const tickValues = Array.from({ length: ticks }, (_, index) =>
    minValue + (index / (ticks - 1)) * valueRange,
  );

  const formatValue = valueFormatter ?? ((value: number) => value.toFixed(2));

  return (
    <div className="analytics-chart">
      <svg
        className="analytics-chart__svg"
        viewBox={`0 0 ${chartWidth} ${chartHeight}`}
        role="img"
        aria-label="Metric trend chart"
      >
        <defs>
          <linearGradient id="trend-fill" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={color} stopOpacity="0.35" />
            <stop offset="100%" stopColor={color} stopOpacity="0" />
          </linearGradient>
        </defs>

        <g className="analytics-chart__grid">
          {tickValues.map((tickValue) => {
            const y = mapY(tickValue);
            return (
              <g key={`grid-${tickValue}`}>
                <line
                  x1={margin.left}
                  x2={chartWidth - margin.right}
                  y1={y}
                  y2={y}
                />
                <text x={margin.left - 8} y={y} dy="0.35em">
                  {formatValue(tickValue)}
                </text>
              </g>
            );
          })}
        </g>

        <path
          d={`${path} L${mapX(maxTimestamp)} ${margin.top + innerHeight} L${mapX(
            minTimestamp,
          )} ${margin.top + innerHeight} Z`}
          fill="url(#trend-fill)"
          className="analytics-chart__area"
        />
        <path d={path} stroke={color} className="analytics-chart__line" />

        {points.map((point) => (
          <circle
            key={point.iso}
            cx={mapX(point.timestamp)}
            cy={mapY(point.value)}
            r={3.5}
            fill={color}
          />
        ))}

        <text
          className="analytics-chart__unit"
          x={chartWidth - margin.right}
          y={margin.top - 6}
        >
          {unit}
        </text>
      </svg>
    </div>
  );
}

export {
  CostBreakdownTable,
  AnalyticsLineChart,
  MetricCard,
  PerformanceTable,
  UsageTable,
};
