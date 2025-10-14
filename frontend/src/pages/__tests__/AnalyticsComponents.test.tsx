import { render, screen } from "@testing-library/react";
import type {
  CostBreakdown,
  PerformanceStatistics,
  UsageStatistics,
} from "../../api/types";
import {
  AnalyticsLineChart,
  CostBreakdownTable,
  MetricCard,
  PerformanceTable,
  UsageTable,
} from "../AnalyticsDashboardPage";

describe("MetricCard", () => {
  it("renders formatted value", () => {
    render(
      <MetricCard
        title="Total Cost"
        value={123.456}
        unit="USD"
        isLoading={false}
        formatter={(value) => `$${value.toFixed(1)}`}
      />,
    );

    expect(screen.getByText("Total Cost")).toBeInTheDocument();
    expect(screen.getByText("$123.5")).toBeInTheDocument();
    expect(screen.getByText("USD")).toBeInTheDocument();
  });

  it("renders loading state", () => {
    render(
      <MetricCard
        title="Tokens"
        value={undefined}
        unit="tokens"
        isLoading
      />,
    );

    expect(screen.getByText("Loading…")).toBeInTheDocument();
  });
});

describe("UsageTable", () => {
  const usage: UsageStatistics = {
    user_id: "user-1",
    total_api_calls: 120,
    total_tokens: 4500,
    total_cost: 18.75,
    avg_response_time_ms: 235.4,
    error_rate: 0.12,
    period_start: new Date().toISOString(),
    period_end: new Date().toISOString(),
    quotas: [],
  };

  const formatNumber = (value: number, fractionDigits = 2) =>
    value.toFixed(fractionDigits);
  const formatPercent = (value: number) => `${(value * 100).toFixed(1)}%`;

  it("shows usage rows", () => {
    render(
      <UsageTable
        usage={usage}
        isLoading={false}
        error={undefined}
        formatNumber={formatNumber}
        formatPercent={formatPercent}
      />,
    );

    expect(screen.getByText("API Calls")).toBeInTheDocument();
    expect(screen.getByText("120")).toBeInTheDocument();
    expect(screen.getByText("Tokens Consumed")).toBeInTheDocument();
    expect(screen.getByText("4500")).toBeInTheDocument();
    expect(screen.getByText("Total Cost")).toBeInTheDocument();
    expect(screen.getByText("$18.75")).toBeInTheDocument();
    expect(screen.getByText("Error Rate")).toBeInTheDocument();
    expect(screen.getByText("12.0%"))
      .toBeInTheDocument();
  });

  it("renders error placeholder", () => {
    render(
      <UsageTable
        usage={undefined}
        isLoading={false}
        error="failed to load"
        formatNumber={formatNumber}
        formatPercent={formatPercent}
      />,
    );

    expect(screen.getByText("failed to load")).toBeInTheDocument();
  });
});

describe("PerformanceTable", () => {
  const formatNumber = (value: number, fractionDigits = 2) =>
    value.toFixed(fractionDigits);

  it("renders informative placeholder when loading", () => {
    render(
      <PerformanceTable
        statistics={undefined}
        isLoading
        error={undefined}
        formatNumber={formatNumber}
      />,
    );

    expect(screen.getByText("Loading performance data…")).toBeInTheDocument();
  });

  it("renders statistics rows", () => {
    const stats: PerformanceStatistics = {
      operation: "agent.run",
      total_calls: 20,
      success_count: 18,
      error_count: 2,
      avg_duration_ms: 210,
      min_duration_ms: 120,
      max_duration_ms: 380,
      p50_duration_ms: 205,
      p95_duration_ms: 350,
      p99_duration_ms: 380,
      period_start: new Date().toISOString(),
      period_end: new Date().toISOString(),
    };

    render(
      <PerformanceTable
        statistics={stats}
        isLoading={false}
        error={undefined}
        formatNumber={formatNumber}
      />,
    );

    expect(screen.getByText("agent.run")).toBeInTheDocument();
    expect(screen.getByText("20")).toBeInTheDocument();
    expect(screen.getByText("18")).toBeInTheDocument();
    expect(screen.getByText("2")).toBeInTheDocument();
  });

  it("renders error state", () => {
    render(
      <PerformanceTable
        statistics={undefined}
        isLoading={false}
        error="could not fetch"
        formatNumber={formatNumber}
      />,
    );

    expect(screen.getByText("could not fetch")).toBeInTheDocument();
  });
});

describe("CostBreakdownTable", () => {
  const breakdown: CostBreakdown = {
    entity_id: "agent-1",
    entity_type: "agent",
    total_cost: 42.5,
    total_tokens: 3200,
    api_calls: 128,
    period_start: new Date().toISOString(),
    period_end: new Date().toISOString(),
    breakdown: { model: { "gpt-4o-mini": 42.5 } },
  };

  const formatNumber = (value: number, fractionDigits = 2) =>
    value.toFixed(fractionDigits);

  it("requests entity input when no data", () => {
    render(
      <CostBreakdownTable
        breakdown={undefined}
        isLoading={false}
        error={undefined}
        formatNumber={formatNumber}
      />,
    );

    expect(
      screen.getByText("Provide an entity ID to view costs"),
    ).toBeInTheDocument();
  });

  it("renders cost details", () => {
    render(
      <CostBreakdownTable
        breakdown={breakdown}
        isLoading={false}
        error={undefined}
        formatNumber={formatNumber}
      />,
    );

    expect(screen.getByText("agent-1")).toBeInTheDocument();
    expect(screen.getByText("$42.50")).toBeInTheDocument();
    expect(screen.getByText("128")).toBeInTheDocument();
    expect(screen.getByText(/gpt-4o-mini/)).toBeInTheDocument();
  });

  it("renders error placeholder", () => {
    render(
      <CostBreakdownTable
        breakdown={undefined}
        isLoading={false}
        error="unable to compute"
        formatNumber={formatNumber}
      />,
    );

    expect(screen.getByText("unable to compute")).toBeInTheDocument();
  });
});

describe("AnalyticsLineChart", () => {
  const points = [
    { timestamp: Date.now() - 86_400_000, iso: new Date(Date.now() - 86_400_000).toISOString(), value: 5 },
    { timestamp: Date.now(), iso: new Date().toISOString(), value: 10 },
  ];

  it("renders loading placeholder", () => {
    render(
      <AnalyticsLineChart
        points={[]}
        isLoading
        color="#38bdf8"
        unit="USD"
      />,
    );

    expect(screen.getByText("Loading trend data…")).toBeInTheDocument();
  });

  it("shows chart when data exists", () => {
    render(
      <AnalyticsLineChart
        points={points}
        isLoading={false}
        color="#38bdf8"
        unit="USD"
        valueFormatter={(value) => `$${value.toFixed(2)}`}
      />,
    );

    expect(screen.getByLabelText("Metric trend chart")).toBeInTheDocument();
  });

  it("renders error state", () => {
    render(
      <AnalyticsLineChart
        points={[]}
        isLoading={false}
        error="trend error"
        color="#38bdf8"
        unit="USD"
      />,
    );

    expect(screen.getByText("trend error")).toBeInTheDocument();
  });

  it("renders no-data placeholder", () => {
    render(
      <AnalyticsLineChart
        points={[]}
        isLoading={false}
        color="#38bdf8"
        unit="USD"
      />,
    );

    expect(screen.getByText("No data in the selected range.")).toBeInTheDocument();
  });
});
