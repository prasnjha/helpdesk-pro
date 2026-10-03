// Redirects to /login without a token (frontend/CLAUDE.md, E2-S4).

import type { JSX } from "react";
import { Navigate } from "react-router-dom";

import { getToken } from "../state/session";

interface AuthGuardProps {
  children: JSX.Element;
}

export function AuthGuard({ children }: AuthGuardProps): JSX.Element {
  const token = getToken();
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  return children;
}
