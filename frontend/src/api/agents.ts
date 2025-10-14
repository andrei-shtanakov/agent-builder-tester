import { apiFetch } from "./client";
import type { Agent } from "./types";

export const fetchAgents = (): Promise<Agent[]> => apiFetch<Agent[]>("/agents");
