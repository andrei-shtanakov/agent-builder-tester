import { create } from "zustand";
import type { User } from "../api/types";

type AuthStatus = "checking" | "authenticated" | "unauthenticated";

const STORAGE_KEY = "agents-studio-auth-token";

const readTokenFromStorage = (): string | null => {
  if (typeof window === "undefined") {
    return null;
  }
  try {
    return window.localStorage.getItem(STORAGE_KEY);
  } catch (error) {
    console.warn("Failed to read token from storage", error);
    return null;
  }
};

export const FALLBACK_USER: User = {
  id: "00000000-0000-0000-0000-000000000000",
  email: "guest@example.com",
  username: "guest",
  full_name: "Guest User",
  is_active: true,
  is_superuser: false,
  created_at: new Date(0).toISOString(),
  updated_at: new Date(0).toISOString(),
  last_login: null,
};

const initialToken = readTokenFromStorage();
const initialStatus: AuthStatus = initialToken ? "checking" : "authenticated";

interface AuthState {
  token: string | null;
  user: User | null;
  status: AuthStatus;
  error: string | null;
  initialized: boolean;
  hasCheckedProfile: boolean;
  setToken: (token: string) => void;
  clearToken: () => void;
  setError: (message: string | null) => void;
  markProfileChecked: () => void;
  reloadToken: () => void;
  completeAuthentication: (user: User) => void;
  failAuthentication: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  token: initialToken,
  user: initialToken ? FALLBACK_USER : FALLBACK_USER,
  status: initialStatus,
  error: null,
  initialized: true,
  hasCheckedProfile: initialToken ? false : true,
  setToken: (token: string) => {
    if (typeof window !== "undefined") {
      window.localStorage.setItem(STORAGE_KEY, token);
    }
    set({
      token,
      status: "checking",
      error: null,
      user: FALLBACK_USER,
      initialized: true,
      hasCheckedProfile: false,
    });
  },
  clearToken: () => {
    if (typeof window !== "undefined") {
      window.localStorage.removeItem(STORAGE_KEY);
    }
    set((state) => ({
      token: null,
      user: FALLBACK_USER,
      status: "authenticated",
      error: state.error,
      initialized: true,
      hasCheckedProfile: true,
    }));
  },
  setError: (message: string | null) => {
    set({ error: message });
  },
  completeAuthentication: (user: User) => {
    set({
      user: user ?? FALLBACK_USER,
      status: "authenticated",
      error: null,
      hasCheckedProfile: true,
    });
  },
  failAuthentication: () => {
    set((state) => ({
      user: FALLBACK_USER,
      status: "authenticated",
      error: state.error,
      hasCheckedProfile: true,
    }));
  },
  markProfileChecked: () => {
    set(() => ({ hasCheckedProfile: true }));
  },
  reloadToken: () => {
    const storedToken = readTokenFromStorage();
    set({
      token: storedToken,
      status: storedToken ? "checking" : "unauthenticated",
      error: null,
      user: storedToken ? FALLBACK_USER : FALLBACK_USER,
      initialized: true,
      hasCheckedProfile: storedToken ? false : true,
    });
  },
}));
