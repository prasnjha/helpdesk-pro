// Minimal sign-in page (component-map.md, E2-S4).

import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { ApiError, apiRequest } from "../api/client";
import type { LoginResponse } from "../api/types";
import { ErrorBanner } from "../components/ErrorBanner";
import { setToken } from "../state/session";

export function LoginPage(): JSX.Element {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  async function handleSubmit(event: React.FormEvent): Promise<void> {
    event.preventDefault();
    setError(null);
    try {
      const response = await apiRequest<LoginResponse>("/api/auth/login", {
        method: "POST",
        body: { username, password },
        auth: false,
      });
      setToken(response.token);
      navigate("/tickets");
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError("Unable to reach the server.");
      }
    }
  }

  return (
    <main>
      <h1>Sign in</h1>
      <ErrorBanner message={error} />
      <form onSubmit={(e) => void handleSubmit(e)}>
        <label htmlFor="username">Username</label>
        <input id="username" value={username} onChange={(e) => setUsername(e.target.value)} />

        <label htmlFor="password">Password</label>
        <input
          id="password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        <button type="submit">Sign in</button>
      </form>
    </main>
  );
}
