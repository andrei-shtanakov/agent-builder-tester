import { useEffect, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { buildWebSocketUrl } from "../api/client";

export type ChatSocketState = "idle" | "connecting" | "open" | "closed" | "error";

export const useChatSocket = (conversationId: string | null): ChatSocketState => {
  const queryClient = useQueryClient();
  const [socketState, setSocketState] = useState<ChatSocketState>("idle");

  useEffect(() => {
    if (!conversationId) {
      setSocketState("idle");
      return;
    }

    let isActive = true;
    setSocketState("connecting");

    const socket = new WebSocket(buildWebSocketUrl(`/chat/${conversationId}`));

    socket.addEventListener("open", () => {
      if (!isActive) {
        return;
      }
      setSocketState("open");
      socket.send(JSON.stringify({ type: "subscribe" }));
    });

    socket.addEventListener("message", (event) => {
      if (!isActive) {
        return;
      }

      try {
        const payload = JSON.parse(event.data) as { type?: string };
        if (payload.type === "message") {
          queryClient.invalidateQueries({
            queryKey: ["chat", "messages", conversationId],
          });
        } else if (payload.type === "ping") {
          socket.send(JSON.stringify({ type: "pong" }));
        }
      } catch (error) {
        console.warn("Failed to parse chat socket payload", error);
      }
    });

    socket.addEventListener("error", () => {
      if (!isActive) {
        return;
      }
      setSocketState("error");
    });

    socket.addEventListener("close", () => {
      if (!isActive) {
        return;
      }
      setSocketState("closed");
    });

    return () => {
      isActive = false;
      socket.close();
    };
  }, [conversationId, queryClient]);

  return socketState;
};
