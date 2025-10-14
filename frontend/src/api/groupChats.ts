import { apiFetch } from "./client";
import type { GroupChat, Message } from "./types";

export const fetchGroupChats = (): Promise<GroupChat[]> =>
  apiFetch<GroupChat[]>("/group-chats");

export const fetchGroupChatMessages = (
  groupChatId: string,
): Promise<Message[]> =>
  apiFetch<Message[]>(`/group-chats/${groupChatId}/messages`);
