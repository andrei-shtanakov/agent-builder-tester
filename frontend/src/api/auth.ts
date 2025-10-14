import { apiFetch } from "./client";
import type { TokenResponse, User } from "./types";

export interface LoginCredentials {
  username: string;
  password: string;
}

export const login = (credentials: LoginCredentials): Promise<TokenResponse> => {
  const formData = new URLSearchParams();
  formData.set("username", credentials.username);
  formData.set("password", credentials.password);

  return apiFetch<TokenResponse>("/auth/login", {
    method: "POST",
    body: formData,
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
  });
};

export const fetchCurrentUser = (): Promise<User> => apiFetch<User>("/auth/me");
