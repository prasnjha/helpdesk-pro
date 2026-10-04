// Sign-in page (component-map.md, E2-S4), laid out after login.png: a
// centred card with the brand mark. No AppShell here (no session yet).

import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { ApiError, apiRequest } from "../api/client";
import type { LoginResponse } from "../api/types";
import { ErrorBanner } from "../components/ErrorBanner";
import { Icon } from "../components/Icon";
import { setSession } from "../state/session";

const HOME_BY_ROLE: Record<string, string> = {
  customer: "/tickets",
  agent: "/agent/queues/billing",
  admin: "/admin/sla-policies",
};

function LoginBrand(): JSX.Element {
  return (
    <div className="login-brand">
      <span className="login-logo-tile">
        <img src="/helpdesk-pro-logo.png" alt="HelpDesk Pro" className="login-logo" />
      </span>
      <p className="login-product">HelpDesk Pro</p>
      <p className="login-subtitle">Sign in to manage support tickets, SLAs and the knowledge base.</p>
    </div>
  );
}

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
      setSession(response.token, response.role, response.username);
      navigate(HOME_BY_ROLE[response.role] ?? "/tickets");
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError("Unable to reach the server.");
      }
    }
  }

  return (
    <div className="login-screen">
      <main className="login-main">
        <div className="card login-card">
          <LoginBrand />
          <h1 className="login-title">Sign in</h1>
          <ErrorBanner message={error} />
          <form onSubmit={(e) => void handleSubmit(e)} className="login-form">
            <div className="field">
              <label htmlFor="username">Username</label>
              <input
                id="username"
                autoComplete="username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
              />
            </div>

            <div className="field">
              <label htmlFor="password">Password</label>
              <input
                id="password"
                type="password"
                autoComplete="current-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>

            <button type="submit" className="login-submit">
              Sign in
              <Icon name="arrowLeft" size={18} className="icon-flip" />
            </button>
          </form>
        </div>
        <p className="login-footnote">
          <Icon name="lock" size={16} />
          Synthetic demo data only
        </p>
      </main>
    </div>
  );
}
