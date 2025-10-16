import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  createAgent,
  deleteAgent,
  fetchAgents,
  fetchAgentTemplates,
} from "../api/agents";
import type { Agent, AgentCreate, AgentTemplate } from "../api/types";
import { PromptEditor } from "../components/PromptEditor";
import { ToolConfiguration } from "../components/ToolConfiguration";
import { TestHarness } from "../components/TestHarness";

type ViewMode = "list" | "create" | "edit";

export function AgentManagementPage(): JSX.Element {
  const [viewMode, setViewMode] = useState<ViewMode>("list");
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);
  const [formData, setFormData] = useState<AgentCreate>({
    name: "",
    description: "",
    type: "assistant",
    status: "draft",
    initial_config: {
      system_message: "",
      temperature: 0.7,
      max_tokens: 1000,
    },
  });

  const queryClient = useQueryClient();

  const { data: agents = [], isLoading: isLoadingAgents } = useQuery({
    queryKey: ["agents"],
    queryFn: fetchAgents,
  });

  const { data: templates = [] } = useQuery({
    queryKey: ["agent-templates"],
    queryFn: fetchAgentTemplates,
  });

  const createMutation = useMutation({
    mutationFn: createAgent,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["agents"] });
      setViewMode("list");
      resetForm();
    },
  });

  const deleteMutation = useMutation({
    mutationFn: deleteAgent,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["agents"] });
    },
  });

  const resetForm = () => {
    setFormData({
      name: "",
      description: "",
      type: "assistant",
      status: "draft",
      initial_config: {
        system_message: "",
        temperature: 0.7,
        max_tokens: 1000,
      },
    });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    createMutation.mutate(formData);
  };

  const handleTemplateSelect = (template: AgentTemplate) => {
    setFormData((prev) => ({
      ...prev,
      name: template.name,
      description: template.description,
      initial_config: template.config,
    }));
  };

  const handleSystemMessageChange = (value: string) => {
    setFormData((prev) => ({
      ...prev,
      initial_config: {
        ...(prev.initial_config as Record<string, unknown>),
        system_message: value,
      },
    }));
  };

  const handleToolsChange = (tools: string[]) => {
    setFormData((prev) => ({
      ...prev,
      initial_config: {
        ...(prev.initial_config as Record<string, unknown>),
        tools,
      },
    }));
  };

  const handleDelete = (agentId: string) => {
    if (window.confirm("Are you sure you want to delete this agent?")) {
      deleteMutation.mutate(agentId);
    }
  };

  if (viewMode === "list") {
    return (
      <div className="agent-management">
        <div className="agent-management__header">
          <h1>Agent Management</h1>
          <button
            type="button"
            className="button button--primary"
            onClick={() => setViewMode("create")}
          >
            Create Agent
          </button>
        </div>

        {isLoadingAgents ? (
          <div className="loading">Loading agents...</div>
        ) : (
          <div className="agent-list">
            {agents.map((agent) => (
              <div key={agent.id} className="agent-card">
                <div className="agent-card__header">
                  <h3>{agent.name}</h3>
                  <span className={`agent-card__status agent-card__status--${agent.status}`}>
                    {agent.status}
                  </span>
                </div>
                <p className="agent-card__description">
                  {agent.description || "No description"}
                </p>
                <div className="agent-card__meta">
                  <span>Type: {agent.type}</span>
                  <span>Versions: {agent.versions.length}</span>
                </div>
                <div className="agent-card__actions">
                  <button
                    type="button"
                    className="button button--secondary"
                    onClick={() => {
                      setSelectedAgent(agent);
                      setViewMode("edit");
                    }}
                  >
                    Edit
                  </button>
                  <button
                    type="button"
                    className="button button--ghost"
                    onClick={() => handleDelete(agent.id)}
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
            {agents.length === 0 && (
              <div className="empty-state">
                No agents yet. Create your first agent to get started.
              </div>
            )}
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="agent-management">
      <div className="agent-management__header">
        <h1>{viewMode === "create" ? "Create Agent" : "Edit Agent"}</h1>
        <button
          type="button"
          className="button button--ghost"
          onClick={() => {
            setViewMode("list");
            resetForm();
          }}
        >
          Back to List
        </button>
      </div>

      <form onSubmit={handleSubmit} className="agent-form">
        <div className="agent-form__section">
          <h2>Basic Information</h2>

          <div className="form-group">
            <label htmlFor="name">Name *</label>
            <input
              id="name"
              type="text"
              value={formData.name}
              onChange={(e) =>
                setFormData((prev) => ({ ...prev, name: e.target.value }))
              }
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="description">Description</label>
            <textarea
              id="description"
              value={formData.description || ""}
              onChange={(e) =>
                setFormData((prev) => ({
                  ...prev,
                  description: e.target.value,
                }))
              }
              rows={3}
            />
          </div>

          <div className="form-group">
            <label htmlFor="type">Type *</label>
            <select
              id="type"
              value={formData.type}
              onChange={(e) =>
                setFormData((prev) => ({ ...prev, type: e.target.value }))
              }
              required
            >
              <option value="assistant">Assistant</option>
              <option value="user_proxy">User Proxy</option>
              <option value="group_chat_manager">Group Chat Manager</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="template">Use Template</label>
            <select
              id="template"
              onChange={(e) => {
                const template = templates.find((t) => t.id === e.target.value);
                if (template) handleTemplateSelect(template);
              }}
            >
              <option value="">-- Select Template --</option>
              {templates.map((template) => (
                <option key={template.id} value={template.id}>
                  {template.name}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="agent-form__section">
          <h2>System Prompt</h2>
          <PromptEditor
            value={
              (formData.initial_config as Record<string, string>)?.system_message || ""
            }
            onChange={handleSystemMessageChange}
          />
        </div>

        <div className="agent-form__section">
          <h2>Tools & MCP Configuration</h2>
          <ToolConfiguration
            selectedTools={
              ((formData.initial_config as Record<string, unknown>)?.tools as string[]) || []
            }
            onChange={handleToolsChange}
          />
        </div>

        {viewMode === "create" && formData.name && (
          <div className="agent-form__section">
            <h2>Test Agent</h2>
            <TestHarness
              agentName={formData.name}
              config={formData.initial_config || {}}
            />
          </div>
        )}

        <div className="agent-form__actions">
          <button
            type="button"
            className="button button--ghost"
            onClick={() => {
              setViewMode("list");
              resetForm();
            }}
          >
            Cancel
          </button>
          <button
            type="submit"
            className="button button--primary"
            disabled={createMutation.isPending}
          >
            {createMutation.isPending ? "Creating..." : "Create Agent"}
          </button>
        </div>
      </form>
    </div>
  );
}

