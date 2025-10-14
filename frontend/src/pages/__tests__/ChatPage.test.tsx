import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { vi, type Mock } from "vitest";
import { ChatPage } from "../ChatPage";
import {
  fetchConversations,
  fetchConversationMessages,
  createConversation,
  sendConversationMessage,
} from "../../api/chat";
import { fetchAgents } from "../../api/agents";
import { fetchLogs } from "../../api/logs";
import { useChatSocket } from "../../hooks/useChatSocket";
import { useLogSocket } from "../../hooks/useLogSocket";

vi.mock("../../api/agents", () => ({
  fetchAgents: vi.fn(),
}));

vi.mock("../../api/chat", () => ({
  fetchConversations: vi.fn(),
  fetchConversationMessages: vi.fn(),
  createConversation: vi.fn(),
  sendConversationMessage: vi.fn(),
}));

vi.mock("../../api/logs", () => ({
  fetchLogs: vi.fn(),
}));

vi.mock("../../hooks/useChatSocket", () => ({
  useChatSocket: vi.fn(),
}));

vi.mock("../../hooks/useLogSocket", () => ({
  useLogSocket: vi.fn(),
}));

const fetchAgentsMock = fetchAgents as unknown as Mock;
const fetchConversationsMock = fetchConversations as unknown as Mock;
const fetchConversationMessagesMock =
  fetchConversationMessages as unknown as Mock;
const createConversationMock = createConversation as unknown as Mock;
const sendConversationMessageMock =
  sendConversationMessage as unknown as Mock;
const fetchLogsMock = fetchLogs as unknown as Mock;
const useChatSocketMock = useChatSocket as unknown as Mock;
const useLogSocketMock = useLogSocket as unknown as Mock;

const renderChatPage = () => {
  const queryClient = new QueryClient();
  return render(
    <QueryClientProvider client={queryClient}>
      <ChatPage />
    </QueryClientProvider>,
  );
};

describe("ChatPage", () => {
  beforeEach(() => {
    fetchAgentsMock.mockReset();
    fetchConversationsMock.mockReset();
    fetchConversationMessagesMock.mockReset();
    createConversationMock.mockReset();
    sendConversationMessageMock.mockReset();
    fetchLogsMock.mockReset();
    useChatSocketMock.mockReset();
    useLogSocketMock.mockReset();

    fetchAgentsMock.mockResolvedValue([
      {
        id: "agent-1",
        name: "Support Agent",
        description: null,
        type: "assistant",
        status: "active",
        tags: null,
        current_version_id: "version-1",
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        versions: [],
      },
    ]);

    fetchConversationsMock.mockResolvedValue([
      {
        id: "conversation-1",
        agent_id: "agent-1",
        agent_version_id: "version-1",
        title: "Support Chat",
        extra_data: null,
        started_at: new Date("2024-01-01T10:00:00Z").toISOString(),
        ended_at: null,
        status: "active",
        messages: [],
      },
    ]);

    fetchConversationMessagesMock.mockResolvedValue([
      {
        id: "message-1",
        conversation_id: "conversation-1",
        role: "user",
        content: "Hello",
        extra_data: null,
        created_at: new Date("2024-01-01T10:01:00Z").toISOString(),
        parent_message_id: null,
      },
      {
        id: "message-2",
        conversation_id: "conversation-1",
        role: "assistant",
        content: "Hi there!",
        extra_data: null,
        created_at: new Date("2024-01-01T10:01:30Z").toISOString(),
        parent_message_id: null,
      },
    ]);

    createConversationMock.mockResolvedValue({
      id: "conversation-2",
      agent_id: "agent-1",
      agent_version_id: "version-1",
      title: "New Conversation",
      extra_data: null,
      started_at: new Date().toISOString(),
      ended_at: null,
      status: "active",
      messages: [],
    });

    sendConversationMessageMock.mockResolvedValue({
      id: "message-3",
      conversation_id: "conversation-1",
      role: "user",
      content: "Ping",
      extra_data: null,
      created_at: new Date().toISOString(),
      parent_message_id: null,
    });

    fetchLogsMock.mockResolvedValue([
      {
        id: "log-1",
        conversation_id: "conversation-1",
        event_type: "message",
        level: "info",
        agent_name: "Support Agent",
        content: "Execution started",
        data: null,
        timestamp: new Date("2024-01-01T10:00:30Z").toISOString(),
      },
    ]);

    useChatSocketMock.mockReturnValue("open");
    useLogSocketMock.mockImplementation((_, onLog: (log: unknown) => void) => {
      if (typeof onLog === "function") {
        setTimeout(() => {
          onLog({
            id: "log-2",
            conversation_id: "conversation-1",
            event_type: "llm_call",
            level: "debug",
            agent_name: "Support Agent",
            content: "Streaming tokens",
            data: { tokens: 24 },
            timestamp: new Date("2024-01-01T10:00:45Z").toISOString(),
          });
        }, 0);
      }
      return "open";
    });
  });

  it("renders conversations and messages", async () => {
    renderChatPage();

    await waitFor(() => {
      expect(screen.getByText("Support Chat")).toBeInTheDocument();
    });

    await waitFor(() => {
      expect(screen.getByText("Hello")).toBeInTheDocument();
      expect(screen.getByText("Hi there!")).toBeInTheDocument();
      expect(screen.getByText("Execution started")).toBeInTheDocument();
      expect(screen.getByText("Streaming tokens")).toBeInTheDocument();
    });
  });

  it("sends a new message", async () => {
    renderChatPage();

    await waitFor(() => {
      expect(screen.getAllByText("Support Chat").length).toBeGreaterThan(0);
    });

    const input = screen.getByPlaceholderText("Compose a message…");
    fireEvent.change(input, { target: { value: "A new message" } });

    fireEvent.click(screen.getByRole("button", { name: "Send Message" }));

    await waitFor(() => {
      expect(sendConversationMessageMock).toHaveBeenCalledWith(
        "conversation-1",
        expect.objectContaining({
          role: "user",
          content: "A new message",
        }),
      );
    });
  });
});
