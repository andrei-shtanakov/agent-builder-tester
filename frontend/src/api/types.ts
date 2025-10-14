export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface User {
  id: string;
  email: string;
  username: string;
  full_name: string | null;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
  updated_at: string;
  last_login: string | null;
}

export interface AgentVersion {
  id: string;
  agent_id: string;
  version: string;
  config: Record<string, unknown>;
  changelog: string | null;
  created_by: string | null;
  created_at: string;
  is_current: boolean;
}

export interface Agent {
  id: string;
  name: string;
  description: string | null;
  type: string;
  status: string;
  tags: Record<string, unknown> | null;
  current_version_id: string | null;
  created_at: string;
  updated_at: string;
  versions: AgentVersion[];
}

export interface GroupChatParticipant {
  id: string;
  group_chat_id: string;
  agent_id: string;
  agent_version_id: string | null;
  speaking_order: number | null;
  constraints: Record<string, unknown> | null;
  added_at: string;
}

export interface GroupChat {
  id: string;
  title: string;
  description: string | null;
  selection_strategy: string;
  max_rounds: number;
  allow_repeated_speaker: boolean;
  termination_config: Record<string, unknown> | null;
  extra_data: Record<string, unknown> | null;
  status: string;
  created_at: string;
  updated_at: string;
  participants: GroupChatParticipant[];
}

export interface Message {
  id: string;
  conversation_id: string;
  role: string;
  content: string;
  extra_data: Record<string, unknown> | null;
  created_at: string;
  parent_message_id: string | null;
}

export interface Conversation {
  id: string;
  agent_id: string;
  agent_version_id: string | null;
  title: string | null;
  extra_data: Record<string, unknown> | null;
  started_at: string;
  ended_at: string | null;
  status: string;
  messages?: Message[];
}

export type LogLevel = "debug" | "info" | "warning" | "error";

export type EventType =
  | "message"
  | "function_call"
  | "llm_call"
  | "error"
  | "system";

export interface ExecutionLog {
  id: string;
  conversation_id: string;
  event_type: EventType;
  level: LogLevel;
  agent_name: string | null;
  content: string;
  data: Record<string, unknown> | null;
  timestamp: string;
}

export interface LogStats {
  total_logs: number;
  by_level: Record<string, number>;
  by_event_type: Record<string, number>;
  time_range: Record<string, string | null>;
}

export type InteractionNodeType = "agent" | "user" | "system" | "unknown";

export interface InteractionNode {
  id: string;
  label: string;
  type: InteractionNodeType;
  count: number;
  position: { x: number; y: number };
}

export interface InteractionEdge {
  id: string;
  source: string;
  target: string;
  count: number;
}

export interface InteractionGraph {
  nodes: InteractionNode[];
  edges: InteractionEdge[];
}

export interface MetricEvent {
  id: string;
  user_id: string | null;
  agent_id: string | null;
  conversation_id: string | null;
  metric_type: string;
  metric_name: string;
  value: number;
  unit: string | null;
  extra_metadata: Record<string, unknown> | null;
  timestamp: string;
}

export interface MetricsSummary {
  total_events: number;
  total_value: number;
  average_value: number;
  min_value: number;
  max_value: number;
  unit: string | null;
  start_date: string;
  end_date: string;
}

export interface UsageQuota {
  id: string;
  user_id: string;
  quota_type: string;
  limit: number;
  used: number;
  reset_period: string;
  last_reset: string;
  next_reset: string;
  extra_metadata: Record<string, unknown> | null;
  created_at: string;
  updated_at: string;
}

export interface UsageStatistics {
  user_id: string;
  total_api_calls: number;
  total_tokens: number;
  total_cost: number;
  avg_response_time_ms: number;
  error_rate: number;
  period_start: string;
  period_end: string;
  quotas: UsageQuota[];
}

export interface PerformanceStatistics {
  operation: string;
  total_calls: number;
  success_count: number;
  error_count: number;
  avg_duration_ms: number;
  min_duration_ms: number;
  max_duration_ms: number;
  p50_duration_ms: number | null;
  p95_duration_ms: number | null;
  p99_duration_ms: number | null;
  period_start: string;
  period_end: string;
}

export interface CostBreakdown {
  entity_id: string;
  entity_type: "agent" | "conversation";
  total_cost: number;
  total_tokens: number;
  api_calls: number;
  period_start: string;
  period_end: string;
  breakdown: Record<string, unknown> | null;
}
