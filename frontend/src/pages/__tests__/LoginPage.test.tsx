import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { vi, type Mock } from "vitest";
import { LoginPage } from "../LoginPage";
import { useAuthStore } from "../../store/authStore";
import { login } from "../../api/auth";

vi.mock("../../api/auth", () => ({
  login: vi.fn(),
}));

const loginMock = login as unknown as Mock;

const renderWithProviders = (ui: JSX.Element) => {
  const queryClient = new QueryClient();
  return render(
    <QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>,
  );
};

describe("LoginPage", () => {
  beforeEach(() => {
    useAuthStore.setState({
      token: null,
      user: null,
      status: "unauthenticated",
      error: null,
      initialized: true,
      hasCheckedProfile: true,
    });
    loginMock.mockReset();
  });

  it("renders the login form", () => {
    renderWithProviders(<LoginPage />);

    expect(screen.getByLabelText(/username/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /sign in/i })).toBeInTheDocument();
  });

  it("submits credentials and stores the token", async () => {
    loginMock.mockResolvedValue({
      access_token: "test-token",
      token_type: "bearer",
    });

    renderWithProviders(<LoginPage />);

    fireEvent.change(screen.getByLabelText(/username/i), {
      target: { value: "analytics-demo" },
    });
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: "AnalyticsDemo!123" },
    });

    fireEvent.submit(screen.getByRole("button", { name: /sign in/i }).closest("form")!);

    await waitFor(() => {
      expect(loginMock).toHaveBeenCalledWith({
        username: "analytics-demo",
        password: "AnalyticsDemo!123",
      });
    });

    await waitFor(() => {
      const state = useAuthStore.getState();
      expect(state.token).toBe("test-token");
      expect(state.status).toBe("checking");
      expect(state.hasCheckedProfile).toBe(false);
    });
  });

  it("shows an error when credentials are rejected", async () => {
    loginMock.mockRejectedValue(
      new Error("Incorrect username or password"),
    );

    renderWithProviders(<LoginPage />);

    fireEvent.change(screen.getByLabelText(/username/i), {
      target: { value: "wrong-user" },
    });
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: "badpass" },
    });

    fireEvent.submit(screen.getByRole("button", { name: /sign in/i }).closest("form")!);

    await waitFor(() => {
      expect(screen.getByText("Incorrect username or password")).toBeInTheDocument();
    });

    const state = useAuthStore.getState();
    expect(state.status).toBe("unauthenticated");
    expect(state.hasCheckedProfile).toBe(true);
  });
});
