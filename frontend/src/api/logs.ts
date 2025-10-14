import { apiFetch } from "./client";
import type { EventType, ExecutionLog, LogLevel, LogStats } from "./types";

export interface LogQueryParams {
  level?: LogLevel;
  event_type?: EventType;
  agent_name?: string;
  limit?: number;
  offset?: number;
}

const buildQueryString = (params?: LogQueryParams): string => {
  if (!params) {
    return "";
  }

  const search = new URLSearchParams();

  if (params.level) {
    search.set("level", params.level);
  }
  if (params.event_type) {
    search.set("event_type", params.event_type);
  }
  if (params.agent_name) {
    search.set("agent_name", params.agent_name);
  }
  if (typeof params.limit === "number") {
    search.set("limit", params.limit.toString());
  }
  if (typeof params.offset === "number") {
    search.set("offset", params.offset.toString());
  }

  const query = search.toString();
  return query.length > 0 ? `?${query}` : "";
};

export const fetchLogs = (
  conversationId: string,
  params?: LogQueryParams,
): Promise<ExecutionLog[]> =>
  apiFetch<ExecutionLog[]>(
    `/logs/sessions/${conversationId}${buildQueryString(params)}`,
  );

export const fetchLogStats = (conversationId: string): Promise<LogStats> =>
  apiFetch<LogStats>(`/logs/sessions/${conversationId}/stats`);
