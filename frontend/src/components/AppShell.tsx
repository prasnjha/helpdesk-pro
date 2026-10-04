// Shared layout for every signed-in route: Header (brand, user, logout) plus
// the role-based SideNav, with the routed page rendered through <Outlet />.
// Role and username come from state/session.ts, the same source AuthGuard
// uses; access control itself stays in AuthGuard on each route.

import { useState } from "react";
import { Outlet, useLocation, useNavigate } from "react-router-dom";

import { clearSession, getRole, getToken, getUsername } from "../state/session";
import { Header } from "./Header";
import { SideNav } from "./SideNav";

export function AppShell(): JSX.Element {
  const navigate = useNavigate();
  const location = useLocation();
  const [menuOpen, setMenuOpen] = useState(false);
  const [openedAt, setOpenedAt] = useState(location.pathname);

  // Close the drawer whenever the route changes (e.g. a link inside a page).
  if (menuOpen && openedAt !== location.pathname) {
    setMenuOpen(false);
  }

  // No session: AuthGuard inside the outlet redirects to /login; render no
  // chrome around that redirect.
  if (!getToken()) {
    return <Outlet />;
  }

  const role = getRole();
  const username = getUsername() ?? "";

  function handleLogout(): void {
    clearSession();
    navigate("/login", { replace: true });
  }

  function toggleMenu(): void {
    setOpenedAt(location.pathname);
    setMenuOpen((open) => !open);
  }

  return (
    <div className="app-shell">
      <Header
        user={role ? { username, role } : undefined}
        onLogout={handleLogout}
        menuOpen={menuOpen}
        onMenuToggle={toggleMenu}
      />
      <div className="app-body">
        <SideNav role={role} open={menuOpen} onNavigate={() => setMenuOpen(false)} />
        {menuOpen && (
          <div className="app-backdrop" aria-hidden="true" onClick={() => setMenuOpen(false)} />
        )}
        <div className="app-content">
          <Outlet />
        </div>
      </div>
    </div>
  );
}
