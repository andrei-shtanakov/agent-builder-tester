import { useEffect, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { fetchCurrentUser } from "./api/auth";
import { AgentInteractionsPage } from "./pages/AgentInteractionsPage";
import { AnalyticsDashboardPage } from "./pages/AnalyticsDashboardPage";
import { ChatPage } from "./pages/ChatPage";
import { FALLBACK_USER, useAuthStore } from "./store/authStore";

type AppView = "chat" | "interactions" | "analytics";

const parseErrorMessage = (error: unknown): string => {
  if (error instanceof Error) {
    return error.message;
  }
  return "Unable to load the current user profile.";
};

function App(): JSX.Element {
  const [view, setView] = useState<AppView>("chat");
  const token = useAuthStore((state) => state.token);
  const user = useAuthStore((state) => state.user);
  const status = useAuthStore((state) => state.status);
  const error = useAuthStore((state) => state.error);
  const hasCheckedProfile = useAuthStore((state) => state.hasCheckedProfile);
  const setError = useAuthStore((state) => state.setError);
  const clearToken = useAuthStore((state) => state.clearToken);
  const markProfileChecked = useAuthStore((state) => state.markProfileChecked);
  const completeAuthentication = useAuthStore((state) => state.completeAuthentication);
  const failAuthentication = useAuthStore((state) => state.failAuthentication);

  useQuery({
    queryKey: ["auth", "me", token],
    queryFn: fetchCurrentUser,
    enabled: status !== "authenticated" || !user,
    staleTime: Infinity,
    gcTime: Infinity,
    retry: false,
    onSuccess: (currentUser) => {
      completeAuthentication(currentUser);
      markProfileChecked();
    },
    onError: (fetchError) => {
      setError(parseErrorMessage(fetchError));
      clearToken();
      failAuthentication();
      markProfileChecked();
    },
  });

  useEffect(() => {
    if (!hasCheckedProfile && !token) {
      markProfileChecked();
    }
  }, [hasCheckedProfile, markProfileChecked, token]);

  const handleLogout = () => {
    setError(null);
    clearToken();
    setView("interactions");
  };

  const currentUser = user ?? FALLBACK_USER;

  const renderContent = () => {
    switch (view) {
      case "chat":
        return <ChatPage />;
      case "analytics":
        return <AnalyticsDashboardPage />;
      default:
        return <AgentInteractionsPage />;
    }
  };

  return (
    <div className="app-shell">
      <header className="app-shell__header">
        <div className="app-shell__brand">
          <span className="app-shell__title">AutoGen Agent Studio</span>
          <span className="app-shell__subtitle">
            Analytics, chat, and execution insights
          </span>
        </div>
        <div className="app-shell__user">
          <div className="app-shell__user-meta">
          <span className="app-shell__user-name">
              {currentUser.full_name ?? currentUser.username}
          </span>
            <span className="app-shell__user-email">{currentUser.email}</span>
          </div>
          <button
            type="button"
            className="button button--ghost app-shell__logout"
            onClick={handleLogout}
          >
            Log out
          </button>
        </div>
      </header>
      {error ? <div className="app-shell__error">{error}</div> : null}
      <nav className="app-shell__nav">
        <button
          type="button"
          className={
            view === "chat"
              ? "app-shell__nav-btn app-shell__nav-btn--active"
              : "app-shell__nav-btn"
          }
          onClick={() => setView("chat")}
        >
          Chat Sessions
        </button>
        <button
          type="button"
          className={
            view === "interactions"
              ? "app-shell__nav-btn app-shell__nav-btn--active"
              : "app-shell__nav-btn"
          }
          onClick={() => setView("interactions")}
        >
          Agent Interactions
        </button>
        <button
          type="button"
          className={
            view === "analytics"
              ? "app-shell__nav-btn app-shell__nav-btn--active"
              : "app-shell__nav-btn"
          }
          onClick={() => setView("analytics")}
        >
          Analytics Dashboard
        </button>
      </nav>
      {renderContent()}
    </div>
  );
}

export default App;
