import { useMemo } from "react";
import type {
  Agent,
  GroupChat,
  InteractionEdge,
  InteractionGraph,
  InteractionNode,
  InteractionNodeType,
  Message,
} from "../api/types";

interface UseInteractionGraphOptions {
  selectedGroupChatId: string | null;
  groupChats: GroupChat[] | undefined;
  messages: Message[] | undefined;
  agents: Agent[] | undefined;
}

interface InteractionSummary {
  messageCount: number;
  participantCount: number;
  lastMessageAt: string | null;
}

interface UseInteractionGraphResult {
  graph: InteractionGraph | null;
  summary: InteractionSummary;
}

const DEFAULT_SUMMARY: InteractionSummary = {
  messageCount: 0,
  participantCount: 0,
  lastMessageAt: null,
};

const CANVAS_WIDTH = 960;
const CANVAS_HEIGHT = 560;

const NODE_TYPE_LABELS: Record<InteractionNodeType, string> = {
  agent: "Agent",
  user: "User",
  system: "System",
  unknown: "Unknown",
};

const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === "object" && value !== null;

const readStringProperty = (
  record: Record<string, unknown>,
  keys: string[],
): string | null => {
  for (const key of keys) {
    const candidate = record[key];
    if (typeof candidate === "string" && candidate.trim().length > 0) {
      return candidate;
    }
  }
  return null;
};

const makeAgentNodeId = (agentId: string): string => `agent:${agentId}`;
const makeRoleNodeId = (role: string): string => `role:${role}`;

export const useInteractionGraph = (
  options: UseInteractionGraphOptions,
): UseInteractionGraphResult => {
  const { selectedGroupChatId, groupChats, messages, agents } = options;

  return useMemo(() => {
    if (!selectedGroupChatId || !groupChats) {
      return { graph: null, summary: DEFAULT_SUMMARY };
    }

    const selectedGroupChat = groupChats.find(
      (groupChat) => groupChat.id === selectedGroupChatId,
    );

    if (!selectedGroupChat) {
      return { graph: null, summary: DEFAULT_SUMMARY };
    }

    const agentDirectory = new Map<string, Agent>(
      (agents ?? []).map((agent) => [agent.id, agent]),
    );

    type MutableNode = Omit<InteractionNode, "position"> & {
      position?: InteractionNode["position"];
    };

    const nodes = new Map<string, MutableNode>();
    const edges = new Map<string, InteractionEdge>();

    const ensureNode = (
      id: string,
      label: string,
      type: InteractionNodeType,
    ): MutableNode => {
      const existing = nodes.get(id);
      if (existing) {
        return existing;
      }
      const node: MutableNode = { id, label, type, count: 0 };
      nodes.set(id, node);
      return node;
    };

    const ensureEdge = (source: string, target: string): InteractionEdge => {
      const key = `${source}->${target}`;
      const existing = edges.get(key);
      if (existing) {
        return existing;
      }
      const edge: InteractionEdge = { id: key, source, target, count: 0 };
      edges.set(key, edge);
      return edge;
    };

    selectedGroupChat.participants.forEach((participant) => {
      const agentName = agentDirectory.get(participant.agent_id)?.name;
      const label = agentName ?? `Agent ${participant.agent_id.slice(0, 8)}`;
      ensureNode(makeAgentNodeId(participant.agent_id), label, "agent");
    });

    const sortedMessages = [...(messages ?? [])].sort((a, b) =>
      a.created_at.localeCompare(b.created_at),
    );

    if (sortedMessages.length === 0) {
      const nodeList = Array.from(nodes.values());
      if (nodeList.length === 0) {
        return { graph: null, summary: DEFAULT_SUMMARY };
      }

      const positionedNodes: InteractionNode[] = nodeList.map((node) => ({
        ...node,
        position: { x: CANVAS_WIDTH / 2, y: CANVAS_HEIGHT / 2 },
      }));

      return {
        graph: { nodes: positionedNodes, edges: [] },
        summary: {
          messageCount: 0,
          participantCount: selectedGroupChat.participants.length,
          lastMessageAt: null,
        },
      };
    }

    const deriveSenderNode = (message: Message): MutableNode => {
      const extra = isRecord(message.extra_data) ? message.extra_data : {};
      const agentId =
        readStringProperty(extra, [
          "agent_id",
          "agentId",
          "sender_agent_id",
          "senderAgentId",
        ]) ?? null;
      const agentName = readStringProperty(extra, ["agent_name", "agentName"]);

      if (agentId) {
        const nodeId = makeAgentNodeId(agentId);
        const agentLabel =
          agentName ?? agentDirectory.get(agentId)?.name ?? `Agent ${agentId.slice(0, 8)}`;
        return ensureNode(nodeId, agentLabel, "agent");
      }

      if (message.role === "user") {
        const nodeId = makeRoleNodeId("user");
        return ensureNode(nodeId, "User", "user");
      }

      if (message.role === "system") {
        const nodeId = makeRoleNodeId("system");
        return ensureNode(nodeId, "System", "system");
      }

      const fallbackLabel = agentName ?? message.role ?? NODE_TYPE_LABELS.unknown;
      const nodeId = makeRoleNodeId(fallbackLabel.toLowerCase());
      return ensureNode(nodeId, fallbackLabel, "unknown");
    };

    let previousNode: MutableNode | null = null;

    sortedMessages.forEach((message) => {
      const node = deriveSenderNode(message);
      node.count += 1;

      if (previousNode && previousNode.id !== node.id) {
        const edge = ensureEdge(previousNode.id, node.id);
        edge.count += 1;
      }

      previousNode = node;
    });

    const nodeList = Array.from(nodes.values());
    const edgeList = Array.from(edges.values());

    const nodeCount = nodeList.length;
    const radius = Math.max(180, nodeCount * 60);

    const positionedNodes: InteractionNode[] = nodeList.map((node, index) => {
      const angle = (2 * Math.PI * index) / nodeCount - Math.PI / 2;
      const x = CANVAS_WIDTH / 2 + radius * Math.cos(angle);
      const y = CANVAS_HEIGHT / 2 + radius * Math.sin(angle);
      return {
        id: node.id,
        label: node.label,
        type: node.type,
        count: node.count,
        position: { x, y },
      };
    });

    return {
      graph: {
        nodes: positionedNodes,
        edges: edgeList,
      },
      summary: {
        messageCount: sortedMessages.length,
        participantCount: selectedGroupChat.participants.length,
        lastMessageAt: sortedMessages[sortedMessages.length - 1]?.created_at ?? null,
      },
    };
  }, [selectedGroupChatId, groupChats, messages, agents]);
};
