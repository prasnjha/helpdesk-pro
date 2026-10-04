// Redirects to /login without a token (frontend/CLAUDE.md, E2-S4). Optionally
// restricts by role (frontend/CLAUDE.md: "Customer pages never render for
// agents or admins and the reverse", E6-S1/E6-S2).

import type { JSX } from "react";
import { Navigate } from "react-router-dom";

import { getRole, getToken, type Role } from "../state/session";

interface AuthGuardProps {
  children: JSX.Element;
  allow?: Role[];
}

export function AuthGuard({ children, allow }: AuthGuardProps): JSX.Element {
  const token = getToken();
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  if (allow && !allow.includes(getRole() as Role)) {
    return <Navigate to="/login" replace />;
  }
  return children;
}
