import { apiFetch } from "./client";
import type { Conversation, Message } from "./types";

export interface ConversationCreatePayload {
  agent_id: string;
  agent_version_id?: string | null;
  title?: string | null;
  extra_data?: Record<string, unknown> | null;
}

export interface MessageCreatePayload {
  role: string;
  content: string;
  parent_message_id?: string | null;
  extra_data?: Record<string, unknown> | null;
}

export const fetchConversations = (): Promise<Conversation[]> =>
  apiFetch<Conversation[]>("/chat/sessions");

export const createConversation = (
  payload: ConversationCreatePayload,
): Promise<Conversation> =>
  apiFetch<Conversation>("/chat/sessions", {
    method: "POST",
    body: payload,
  });

export const fetchConversationMessages = (
  conversationId: string,
): Promise<Message[]> =>
  apiFetch<Message[]>(`/chat/sessions/${conversationId}/messages`);

export const sendConversationMessage = (
  conversationId: string,
  payload: MessageCreatePayload,
): Promise<Message> =>
  apiFetch<Message>(`/chat/sessions/${conversationId}/messages`, {
    method: "POST",
    body: payload,
  });
