import { useEffect, useState } from "react";
import { buildWebSocketUrl } from "../api/client";
import type { ExecutionLog } from "../api/types";

export type LogSocketState = "idle" | "connecting" | "open" | "closed" | "error";

export const useLogSocket = (
  conversationId: string | null,
  onLog: (log: ExecutionLog) => void,
): LogSocketState => {
  const [socketState, setSocketState] = useState<LogSocketState>("idle");

  useEffect(() => {
    if (!conversationId) {
      setSocketState("idle");
      return;
    }

    let isMounted = true;
    setSocketState("connecting");

    const socket = new WebSocket(buildWebSocketUrl(`/logs/${conversationId}`));

    socket.addEventListener("open", () => {
      if (!isMounted) {
        return;
      }
      setSocketState("open");
      socket.send(JSON.stringify({ type: "subscribe" }));
    });

    socket.addEventListener("message", (event) => {
      if (!isMounted) {
        return;
      }

      try {
        const payload = JSON.parse(event.data) as {
          type?: string;
          data?: ExecutionLog;
        };

        if (payload.type === "log" && payload.data) {
          onLog(payload.data);
        } else if (payload.type === "ping") {
          socket.send(JSON.stringify({ type: "pong" }));
        }
      } catch (error) {
        console.warn("Failed to parse log socket payload", error);
      }
    });

    socket.addEventListener("error", () => {
      if (!isMounted) {
        return;
      }
      setSocketState("error");
    });

    socket.addEventListener("close", () => {
      if (!isMounted) {
        return;
      }
      setSocketState("closed");
    });

    return () => {
      isMounted = false;
      socket.close();
    };
  }, [conversationId, onLog]);

  return socketState;
};
