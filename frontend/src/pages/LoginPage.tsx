import { FormEvent, useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { login, type LoginCredentials } from "../api/auth";
import { useAuthStore } from "../store/authStore";

const normalizeError = (error: unknown): string => {
  if (error instanceof Error) {
    return error.message;
  }
  return "Unable to log in with the provided credentials.";
};

export function LoginPage(): JSX.Element {
  const [username, setUsername] = useState<string>("");
  const [password, setPassword] = useState<string>("");
  const error = useAuthStore((state) => state.error);
  const setToken = useAuthStore((state) => state.setToken);
  const setError = useAuthStore((state) => state.setError);

  const loginMutation = useMutation({
    mutationFn: (credentials: LoginCredentials) => login(credentials),
    onMutate: () => {
      setError(null);
    },
    onSuccess: (data) => {
      setToken(data.access_token);
    },
    onError: (mutationError) => {
      setError(normalizeError(mutationError));
    },
  });

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const trimmedUsername = username.trim();
    if (trimmedUsername.length === 0 || password.length === 0) {
      return;
    }

    try {
      await loginMutation.mutateAsync({
        username: trimmedUsername,
        password,
      });
      setUsername(trimmedUsername);
    } catch {
      // Error state handled via mutation callbacks.
    } finally {
      setPassword("");
    }
  };

  const isSubmitting = loginMutation.isPending;
  const canSubmit = username.trim().length > 0 && password.length > 0 && !isSubmitting;

  return (
    <div className="login-page">
      <div className="login-card">
        <div className="login-card__header">
          <h1>Agents Studio Sign In</h1>
          <p>Authenticate to manage analytics, chat sessions, and live execution logs.</p>
        </div>
        <form className="login-form" onSubmit={handleSubmit}>
          <label className="form-field">
            <span className="form-label">Username</span>
            <input
              className="form-input"
              type="text"
              autoComplete="username"
              value={username}
              onChange={(event) => {
                setUsername(event.target.value);
                if (error) {
                  setError(null);
                }
              }}
              placeholder="analytics-demo"
            />
          </label>
          <label className="form-field">
            <span className="form-label">Password</span>
            <input
              className="form-input"
              type="password"
              autoComplete="current-password"
              value={password}
              onChange={(event) => {
                setPassword(event.target.value);
                if (error) {
                  setError(null);
                }
              }}
              placeholder="Enter your password"
            />
          </label>
          {error ? <div className="login-form__error">{error}</div> : null}
          <button className="button button--primary" type="submit" disabled={!canSubmit}>
            {isSubmitting ? "Signing in…" : "Sign in"}
          </button>
        </form>
        <dl className="login-hint">
          <dt>Demo account</dt>
          <dd>
            Use <code>analytics-demo</code> / <code>AnalyticsDemo!123</code> after running the
            analytics seed script.
          </dd>
        </dl>
      </div>
    </div>
  );
}
