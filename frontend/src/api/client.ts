import { useAuthStore } from "../store/authStore";

const RAW_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api";
const API_BASE_URL = RAW_BASE_URL.replace(/\/$/, "");

const RAW_WS_BASE_URL = import.meta.env.VITE_WS_BASE_URL;

const computeDefaultWebSocketBase = (): string => {
  try {
    const apiUrl = new URL(API_BASE_URL);
    apiUrl.protocol = apiUrl.protocol === "https:" ? "wss:" : "ws:";

    let pathname = apiUrl.pathname;
    if (pathname.endsWith("/")) {
      pathname = pathname.slice(0, -1);
    }
    if (pathname.endsWith("/api")) {
      pathname = pathname.slice(0, -4);
    }

    apiUrl.pathname = `${pathname}/ws`;
    return apiUrl.toString().replace(/\/$/, "");
  } catch (error) {
    console.warn("Unable to derive WebSocket base URL", error);
    return API_BASE_URL.replace(/^http/, "ws").replace(/\/$/, "");
  }
};

const WS_BASE_URL = (
  RAW_WS_BASE_URL && RAW_WS_BASE_URL.trim().length > 0
    ? RAW_WS_BASE_URL
    : computeDefaultWebSocketBase()
).replace(/\/$/, "");

type HttpMethod = "GET" | "POST" | "PUT" | "PATCH" | "DELETE";

interface RequestOptions {
  method?: HttpMethod;
  body?: unknown;
  headers?: Record<string, string>;
  signal?: AbortSignal;
}

const shouldJsonSerialize = (body: unknown): boolean => {
  if (body === null || body === undefined) {
    return false;
  }

  if (body instanceof FormData || body instanceof URLSearchParams) {
    return false;
  }

  if (typeof body === "string") {
    return false;
  }

  if (body instanceof Blob || body instanceof ArrayBuffer) {
    return false;
  }

  if (ArrayBuffer.isView(body)) {
    return false;
  }

  return typeof body === "object";
};

const buildUrl = (path: string): string => {
  if (path.startsWith("http://") || path.startsWith("https://")) {
    return path;
  }
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  return `${API_BASE_URL}${normalizedPath}`;
};

const buildWebSocketUrl = (path: string): string => {
  if (path.startsWith("ws://") || path.startsWith("wss://")) {
    return path;
  }
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  return `${WS_BASE_URL}${normalizedPath}`;
};

export async function apiFetch<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = "GET", body, headers = {}, signal } = options;
  const token = useAuthStore.getState().token;

  const resolvedHeaders: Record<string, string> = {
    Accept: "application/json",
    ...headers,
  };

  if (token) {
    resolvedHeaders.Authorization = `Bearer ${token}`;
  }

  let resolvedBody: BodyInit | undefined;
  if (body !== undefined && body !== null) {
    if (body instanceof FormData || body instanceof URLSearchParams) {
      resolvedBody = body;
    } else if (
      typeof body === "string" ||
      body instanceof Blob ||
      body instanceof ArrayBuffer ||
      ArrayBuffer.isView(body)
    ) {
      resolvedBody = body as BodyInit;
    } else if (shouldJsonSerialize(body)) {
      resolvedBody = JSON.stringify(body);
      if (!("Content-Type" in resolvedHeaders)) {
        resolvedHeaders["Content-Type"] = "application/json";
      }
    } else {
      resolvedBody = body as BodyInit;
    }
  }

  const response = await fetch(buildUrl(path), {
    method,
    headers: resolvedHeaders,
    body: resolvedBody,
    signal,
  });

  if (!response.ok) {
    const errorPayload = await response.text().catch(() => "");
    const detail = errorPayload ? ` - ${errorPayload}` : "";
    throw new Error(
      `Request failed with status ${response.status} (${response.statusText})${detail}`,
    );
  }

  if (response.status === 204) {
    return undefined as T;
  }

  const contentType = response.headers.get("content-type");
  if (contentType && contentType.includes("application/json")) {
    return (await response.json()) as T;
  }

  return (await response.text()) as unknown as T;
}

export { API_BASE_URL, buildWebSocketUrl };
