import { useEffect, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { fetchAgents } from "../api/agents";
import { fetchGroupChats, fetchGroupChatMessages } from "../api/groupChats";
import { AgentInteractionGraph } from "../components/AgentInteractionGraph";
import { GroupChatSelector } from "../components/GroupChatSelector";
import { useInteractionGraph } from "../hooks/useInteractionGraph";
import { useInteractionStore } from "../store/interactionStore";

function formatTimestamp(timestamp: string | null): string {
  if (!timestamp) {
    return "—";
  }
  try {
    return new Intl.DateTimeFormat(undefined, {
      year: "numeric",
      month: "short",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
    }).format(new Date(timestamp));
  } catch (error) {
    console.warn("Failed to format timestamp", error);
    return timestamp;
  }
}

export function AgentInteractionsPage(): JSX.Element {
  const selectedGroupChatId = useInteractionStore(
    (state) => state.selectedGroupChatId,
  );
  const selectGroupChat = useInteractionStore((state) => state.selectGroupChat);

  const agentsQuery = useQuery({
    queryKey: ["agents"],
    queryFn: fetchAgents,
    staleTime: 5 * 60 * 1000,
  });

  const groupChatsQuery = useQuery({
    queryKey: ["groupChats"],
    queryFn: fetchGroupChats,
    staleTime: 60 * 1000,
    refetchInterval: 60 * 1000,
  });

  const messagesQuery = useQuery({
    queryKey: ["groupChatMessages", selectedGroupChatId],
    queryFn: () => fetchGroupChatMessages(selectedGroupChatId as string),
    enabled: Boolean(selectedGroupChatId),
    staleTime: 30 * 1000,
    refetchInterval: 30 * 1000,
  });

  useEffect(() => {
    if (
      !selectedGroupChatId &&
      groupChatsQuery.data &&
      groupChatsQuery.data.length > 0
    ) {
      selectGroupChat(groupChatsQuery.data[0].id);
    }
  }, [groupChatsQuery.data, selectGroupChat, selectedGroupChatId]);

  const interaction = useInteractionGraph({
    selectedGroupChatId,
    groupChats: groupChatsQuery.data,
    messages: messagesQuery.data,
    agents: agentsQuery.data,
  });

  const graphError = useMemo(() => {
    if (groupChatsQuery.error) {
      return (groupChatsQuery.error as Error).message;
    }
    if (messagesQuery.error) {
      return (messagesQuery.error as Error).message;
    }
    return null;
  }, [groupChatsQuery.error, messagesQuery.error]);

  const isGraphLoading =
    groupChatsQuery.isLoading ||
    messagesQuery.isLoading ||
    agentsQuery.isLoading;

  const handleRefresh = () => {
    void groupChatsQuery.refetch();
    if (selectedGroupChatId) {
      void messagesQuery.refetch();
    }
    void agentsQuery.refetch();
  };

  return (
    <div className="page page--agent-interactions">
      <header className="page__header">
        <div>
          <h1>Agent Interaction Visualization</h1>
          <p>
            Inspect how agents collaborate throughout a conversation. Node size tracks
            message volume while edge weight indicates the frequency of message hand-offs.
          </p>
        </div>
      </header>

      <section className="page__section">
        <div className="controls">
          <GroupChatSelector
            groupChats={groupChatsQuery.data}
            selectedId={selectedGroupChatId}
            onChange={selectGroupChat}
            disabled={groupChatsQuery.isLoading}
          />
          <button
            className="button button--secondary controls__refresh"
            type="button"
            onClick={handleRefresh}
            disabled={groupChatsQuery.isRefetching || messagesQuery.isRefetching}
          >
            Refresh Data
          </button>
        </div>
      </section>

      <section className="page__section">
        <div className="metrics">
          <div className="metrics__card">
            <span className="metrics__label">Messages</span>
            <span className="metrics__value">{interaction.summary.messageCount}</span>
          </div>
          <div className="metrics__card">
            <span className="metrics__label">Participants</span>
            <span className="metrics__value">{interaction.summary.participantCount}</span>
          </div>
          <div className="metrics__card">
            <span className="metrics__label">Last Activity</span>
            <span className="metrics__value">
              {formatTimestamp(interaction.summary.lastMessageAt)}
            </span>
          </div>
        </div>
      </section>

      <section className="page__section page__section--stretch">
        <AgentInteractionGraph
          graph={interaction.graph}
          isLoading={isGraphLoading}
          error={graphError}
          onRefresh={handleRefresh}
        />
      </section>
    </div>
  );
}
