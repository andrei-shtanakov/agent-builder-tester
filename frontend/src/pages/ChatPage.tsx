import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";
import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";
import { fetchAgents } from "../api/agents";
import {
  createConversation,
  fetchConversationMessages,
  fetchConversations,
  sendConversationMessage,
  type ConversationCreatePayload,
} from "../api/chat";
import { fetchLogs } from "../api/logs";
import type {
  Agent,
  Conversation,
  ExecutionLog,
  Message,
} from "../api/types";
import { useChatSocket, type ChatSocketState } from "../hooks/useChatSocket";
import { useLogSocket, type LogSocketState } from "../hooks/useLogSocket";

interface ConversationListProps {
  conversations: Conversation[] | undefined;
  selectedId: string | null;
  onSelect: (conversationId: string) => void;
  isLoading: boolean;
  onRefresh: () => void;
}

interface MessageListProps {
  messages: Message[] | undefined;
  isLoading: boolean;
  error: string | null;
  socketState: ChatSocketState;
}

interface MessageComposerProps {
  disabled: boolean;
  onSend: (content: string) => Promise<void>;
}

interface LogFeedProps {
  logs: ExecutionLog[] | undefined;
  isLoading: boolean;
  error: string | null;
  socketState: LogSocketState;
}

const MAX_RECENT_LOGS = 200;

const formatTimestamp = (timestamp: string): string => {
  try {
    return new Intl.DateTimeFormat(undefined, {
      hour: "2-digit",
      minute: "2-digit",
      month: "short",
      day: "2-digit",
    }).format(new Date(timestamp));
  } catch (error) {
    console.warn("Failed to format timestamp", error);
    return timestamp;
  }
};

const getConversationLabel = (conversation: Conversation): string => {
  if (conversation.title && conversation.title.trim().length > 0) {
    return conversation.title;
  }
  return `Conversation ${conversation.started_at.slice(0, 10)}`;
};

const getSocketBadgeLabel = (
  state: ChatSocketState | LogSocketState,
): string => {
  switch (state) {
    case "open":
      return "Live updates";
    case "connecting":
      return "Connecting…";
    case "error":
      return "Realtime connection failed";
    case "closed":
      return "Realtime connection closed";
    default:
      return "";
  }
};

const ConversationList = ({
  conversations,
  selectedId,
  onSelect,
  isLoading,
  onRefresh,
}: ConversationListProps): JSX.Element => {
  const sortedConversations = useMemo(() => {
    if (!conversations) {
      return [];
    }
    return [...conversations].sort(
      (a, b) =>
        new Date(b.started_at).getTime() - new Date(a.started_at).getTime(),
    );
  }, [conversations]);

  return (
    <aside className="chat-sidebar">
      <header className="chat-sidebar__header">
        <h2>Conversations</h2>
        <button
          className="button button--ghost"
          type="button"
          onClick={onRefresh}
          disabled={isLoading}
        >
          Refresh
        </button>
      </header>
      <div className="chat-sidebar__list" role="list">
        {isLoading ? (
          <div className="chat-sidebar__placeholder">Loading conversations…</div>
        ) : sortedConversations.length === 0 ? (
          <div className="chat-sidebar__placeholder">
            Start a conversation to see it listed here.
          </div>
        ) : (
          sortedConversations.map((conversation) => (
            <button
              key={conversation.id}
              type="button"
              className={
                conversation.id === selectedId
                  ? "chat-sidebar__item chat-sidebar__item--active"
                  : "chat-sidebar__item"
              }
              onClick={() => onSelect(conversation.id)}
            >
              <span className="chat-sidebar__item-title">
                {getConversationLabel(conversation)}
              </span>
              <span className="chat-sidebar__item-meta">
                {formatTimestamp(conversation.started_at)}
              </span>
            </button>
          ))
        )}
      </div>
    </aside>
  );
};

const MessageList = ({
  messages,
  isLoading,
  error,
  socketState,
}: MessageListProps): JSX.Element => {
  if (isLoading) {
    return <div className="chat-panel__placeholder">Loading messages…</div>;
  }

  if (error) {
    return <div className="chat-panel__error">{error}</div>;
  }

  if (!messages || messages.length === 0) {
    return (
      <div className="chat-panel__placeholder">
        No messages yet. Send one to begin the conversation.
      </div>
    );
  }

  return (
    <div className="chat-messages" data-socket-state={socketState}>
      {messages.map((message) => (
        <div
          key={message.id}
          className={
            message.role === "user"
              ? "chat-message chat-message--user"
              : "chat-message chat-message--agent"
          }
        >
          <div className="chat-message__meta">
            <span className="chat-message__role">{message.role}</span>
            <span className="chat-message__time">
              {formatTimestamp(message.created_at)}
            </span>
          </div>
          <div className="chat-message__content">{message.content}</div>
        </div>
      ))}
    </div>
  );
};

const MessageComposer = ({
  disabled,
  onSend,
}: MessageComposerProps): JSX.Element => {
  const [draft, setDraft] = useState<string>("");

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const trimmed = draft.trim();
    if (trimmed.length === 0 || disabled) {
      return;
    }

    try {
      await onSend(trimmed);
      setDraft("");
    } catch (error) {
      console.warn("Failed to send message", error);
    }
  };

  return (
    <form className="chat-composer" onSubmit={handleSubmit}>
      <textarea
        className="chat-composer__input"
        value={draft}
        onChange={(event) => setDraft(event.target.value)}
        placeholder="Compose a message…"
        rows={3}
        disabled={disabled}
      />
      <button
        className="button button--primary"
        type="submit"
        disabled={disabled || draft.trim().length === 0}
      >
        {disabled ? "Sending…" : "Send Message"}
      </button>
    </form>
  );
};

const LogFeed = ({
  logs,
  isLoading,
  error,
  socketState,
}: LogFeedProps): JSX.Element => {
  if (isLoading) {
    return <div className="chat-log-panel__placeholder">Streaming logs…</div>;
  }

  if (error) {
    return <div className="chat-log-panel__error">{error}</div>;
  }

  if (!logs || logs.length === 0) {
    return (
      <div className="chat-log-panel__placeholder">
        Logs will appear here as the execution progresses.
      </div>
    );
  }

  return (
    <div className="chat-log-list" data-socket-state={socketState}>
      {logs.map((log) => (
        <article
          key={log.id}
          className={`chat-log-entry chat-log-entry--${log.level}`}
        >
          <header className="chat-log-entry__meta">
            <span className="chat-log-entry__level">{log.level}</span>
            <span className="chat-log-entry__time">
              {formatTimestamp(log.timestamp)}
            </span>
          </header>
          <div className="chat-log-entry__context">
            <span className="chat-log-entry__event">{log.event_type}</span>
            {log.agent_name ? (
              <span className="chat-log-entry__agent">{log.agent_name}</span>
            ) : null}
          </div>
          <p className="chat-log-entry__content">{log.content}</p>
          {log.data ? (
            <pre className="chat-log-entry__data">
              {JSON.stringify(log.data, null, 2)}
            </pre>
          ) : null}
        </article>
      ))}
    </div>
  );
};

export function ChatPage(): JSX.Element {
  const [selectedConversationId, setSelectedConversationId] = useState<string | null>(
    null,
  );
  const [newConversationAgentId, setNewConversationAgentId] =
    useState<string>("");
  const [newConversationTitle, setNewConversationTitle] =
    useState<string>("");
  const [recentLogs, setRecentLogs] = useState<ExecutionLog[]>([]);

  const queryClient = useQueryClient();

  const agentsQuery = useQuery<Agent[], Error>({
    queryKey: ["agents", "chat"],
    queryFn: fetchAgents,
    staleTime: 5 * 60 * 1000,
  });

  const conversationsQuery = useQuery<Conversation[], Error>({
    queryKey: ["chat", "conversations"],
    queryFn: fetchConversations,
    staleTime: 30 * 1000,
    refetchInterval: 60 * 1000,
  });

  useEffect(() => {
    if (
      !newConversationAgentId &&
      agentsQuery.data &&
      agentsQuery.data.length > 0
    ) {
      setNewConversationAgentId(agentsQuery.data[0].id);
    }
  }, [agentsQuery.data, newConversationAgentId]);

  useEffect(() => {
    if (
      !selectedConversationId &&
      conversationsQuery.data &&
      conversationsQuery.data.length > 0
    ) {
      setSelectedConversationId(conversationsQuery.data[0].id);
    }
  }, [conversationsQuery.data, selectedConversationId]);

  useEffect(() => {
    setRecentLogs([]);
  }, [selectedConversationId]);

  const messagesQuery = useQuery<Message[], Error>({
    queryKey: ["chat", "messages", selectedConversationId],
    queryFn: () =>
      fetchConversationMessages(selectedConversationId as string),
    enabled: Boolean(selectedConversationId),
    refetchOnWindowFocus: false,
    staleTime: 10 * 1000,
  });

  const logsQuery = useQuery<ExecutionLog[], Error>({
    queryKey: ["chat", "logs", selectedConversationId],
    queryFn: () => fetchLogs(selectedConversationId as string, { limit: 200 }),
    enabled: Boolean(selectedConversationId),
    refetchInterval: 60 * 1000,
    staleTime: 30 * 1000,
  });

  const chatSocketState = useChatSocket(selectedConversationId);

  const handleRealtimeLog = useCallback((log: ExecutionLog) => {
    setRecentLogs((current) => {
      const next = [log, ...current];
      const unique = new Map<string, ExecutionLog>();
      for (const entry of next) {
        unique.set(entry.id, entry);
      }
      return Array.from(unique.values()).slice(0, MAX_RECENT_LOGS);
    });
  }, []);

  const logSocketState = useLogSocket(selectedConversationId, handleRealtimeLog);

  const createConversationMutation = useMutation({
    mutationFn: createConversation,
    onSuccess: (conversation) => {
      queryClient.invalidateQueries({ queryKey: ["chat", "conversations"] });
      setSelectedConversationId(conversation.id);
    },
  });

  const sendMessageMutation = useMutation({
    mutationFn: ({
      conversationId,
      content,
    }: {
      conversationId: string;
      content: string;
    }) =>
      sendConversationMessage(conversationId, {
        role: "user",
        content,
      }),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: ["chat", "messages", variables.conversationId],
      });
    },
  });

  const selectedConversation = useMemo(() => {
    if (!selectedConversationId || !conversationsQuery.data) {
      return null;
    }
    return conversationsQuery.data.find(
      (conversation) => conversation.id === selectedConversationId,
    ) ?? null;
  }, [conversationsQuery.data, selectedConversationId]);

  const combinedLogs = useMemo(() => {
    const base = logsQuery.data ?? [];
    const merged = [...base, ...recentLogs];
    const unique = new Map<string, ExecutionLog>();
    for (const entry of merged) {
      unique.set(entry.id, entry);
    }
    return Array.from(unique.values()).sort(
      (a, b) =>
        new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime(),
    );
  }, [logsQuery.data, recentLogs]);

  const handleCreateConversation = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const trimmedTitle = newConversationTitle.trim();
    if (!newConversationAgentId) {
      return;
    }

    const agent = agentsQuery.data?.find((item) => item.id === newConversationAgentId);
    const payload: ConversationCreatePayload = {
      agent_id: newConversationAgentId,
      agent_version_id: agent?.current_version_id ?? null,
      title: trimmedTitle.length > 0 ? trimmedTitle : null,
    };

    try {
      await createConversationMutation.mutateAsync(payload);
      setNewConversationTitle("");
    } catch (error) {
      console.warn("Failed to create conversation", error);
    }
  };

  const handleSendMessage = async (content: string) => {
    if (!selectedConversationId) {
      return;
    }
    try {
      await sendMessageMutation.mutateAsync({
        conversationId: selectedConversationId,
        content,
      });
    } catch (error) {
      console.warn("Failed to send message", error);
    }
  };

  const conversationError = conversationsQuery.error
    ? (conversationsQuery.error as Error).message
    : null;
  const messageError = messagesQuery.error
    ? (messagesQuery.error as Error).message
    : null;
  const logsError = logsQuery.error
    ? (logsQuery.error as Error).message
    : null;

  const chatSocketLabel = getSocketBadgeLabel(chatSocketState);
  const logSocketLabel = getSocketBadgeLabel(logSocketState);
  const isLogFeedLoading = logsQuery.isLoading && combinedLogs.length === 0;
  const chatSocketClassName = [
    "chat-panel__socket",
    `chat-panel__socket--${chatSocketState}`,
  ].join(" ");
  const logSocketClassName = [
    "chat-log-panel__socket",
    `chat-log-panel__socket--${logSocketState}`,
  ].join(" ");

  return (
    <div className="chat-page">
      <ConversationList
        conversations={conversationsQuery.data}
        selectedId={selectedConversationId}
        onSelect={setSelectedConversationId}
        isLoading={conversationsQuery.isLoading}
        onRefresh={() => void conversationsQuery.refetch()}
      />
      <section className="chat-panel">
        <header className="chat-panel__header">
          <div>
            <h1>Chat Sessions</h1>
            <p>
              Review prior exchanges and continue conversations with configured
              agents.
            </p>
          </div>
          {chatSocketLabel ? (
            <span className={chatSocketClassName}>{chatSocketLabel}</span>
          ) : null}
        </header>

        <form className="chat-new" onSubmit={handleCreateConversation}>
          <label className="form-field">
            <span className="form-label">Agent</span>
            <select
              className="form-select"
              value={newConversationAgentId}
              onChange={(event) => setNewConversationAgentId(event.target.value)}
              disabled={agentsQuery.isLoading || !agentsQuery.data?.length}
            >
              {agentsQuery.data?.map((agent) => (
                <option key={agent.id} value={agent.id}>
                  {agent.name}
                </option>
              ))}
            </select>
          </label>
          <label className="form-field">
            <span className="form-label">Title</span>
            <input
              className="form-input"
              type="text"
              value={newConversationTitle}
              onChange={(event) => setNewConversationTitle(event.target.value)}
              placeholder="Optional conversation title"
            />
          </label>
          <button
            className="button button--secondary"
            type="submit"
            disabled={
              createConversationMutation.isLoading || !newConversationAgentId
            }
          >
            {createConversationMutation.isLoading
              ? "Creating…"
              : "Start Conversation"}
          </button>
        </form>

        {conversationError ? (
          <div className="chat-panel__error">{conversationError}</div>
        ) : null}

        {selectedConversation ? (
          <div className="chat-panel__body">
            <div className="chat-panel__conversation-meta">
              <h2>{getConversationLabel(selectedConversation)}</h2>
              <span>
                Started {formatTimestamp(selectedConversation.started_at)}
              </span>
            </div>
            <MessageList
              messages={messagesQuery.data}
              isLoading={messagesQuery.isLoading}
              error={messageError}
              socketState={chatSocketState}
            />
            <MessageComposer
              disabled={sendMessageMutation.isLoading || !selectedConversationId}
              onSend={handleSendMessage}
            />
            <div className="chat-log-panel">
              <div className="chat-log-panel__header">
                <h3>Execution Logs</h3>
                {logSocketLabel ? (
                  <span className={logSocketClassName}>{logSocketLabel}</span>
                ) : null}
              </div>
              <LogFeed
                logs={combinedLogs}
                isLoading={isLogFeedLoading}
                error={logsError}
                socketState={logSocketState}
              />
            </div>
          </div>
        ) : (
          <div className="chat-panel__placeholder">
            Select or create a conversation to view messages.
          </div>
        )}
      </section>
    </div>
  );
}

export { ConversationList, MessageList, MessageComposer, LogFeed };
