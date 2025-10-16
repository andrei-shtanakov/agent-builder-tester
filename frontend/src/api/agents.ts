import { apiFetch } from "./client";
import type {
  Agent,
  AgentCreate,
  AgentTemplate,
  AgentTestRequest,
  AgentTestResponse,
  AgentUpdate,
  AgentVersion,
  AgentVersionCreate,
} from "./types";

export const fetchAgents = (): Promise<Agent[]> => apiFetch<Agent[]>("/agents");

export const fetchAgent = (id: string): Promise<Agent> =>
  apiFetch<Agent>(`/agents/${id}`);

export const createAgent = (data: AgentCreate): Promise<Agent> =>
  apiFetch<Agent>("/agents", {
    method: "POST",
    body: JSON.stringify(data),
  });

export const updateAgent = (id: string, data: AgentUpdate): Promise<Agent> =>
  apiFetch<Agent>(`/agents/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });

export const deleteAgent = (id: string): Promise<void> =>
  apiFetch<void>(`/agents/${id}`, {
    method: "DELETE",
  });

export const createAgentVersion = (
  agentId: string,
  data: AgentVersionCreate
): Promise<AgentVersion> =>
  apiFetch<AgentVersion>(`/agents/${agentId}/versions`, {
    method: "POST",
    body: JSON.stringify(data),
  });

export const testAgent = (
  agentId: string,
  data: AgentTestRequest
): Promise<AgentTestResponse> =>
  apiFetch<AgentTestResponse>(`/agents/${agentId}/test`, {
    method: "POST",
    body: JSON.stringify(data),
  });

export const fetchAgentTemplates = (): Promise<AgentTemplate[]> =>
  apiFetch<AgentTemplate[]>("/agent-templates");

export const fetchAgentTemplate = (id: string): Promise<AgentTemplate> =>
  apiFetch<AgentTemplate>(`/agent-templates/${id}`);
