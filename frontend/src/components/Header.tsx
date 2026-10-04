// Shared header: logo + product name (DESIGN.md Section 5.6 nav anchors,
// frontend/CLAUDE.md "the logo ... for the header and login page"). Inside
// the AppShell it also carries the drawer toggle (below 1024 px), the
// signed-in username and role, and the logout control. Rendered with no
// props it is just the brand bar.

import { Icon } from "./Icon";

const ROLE_LABEL: Record<string, string> = {
  customer: "Customer",
  agent: "Agent",
  admin: "Admin",
};

export interface HeaderUser {
  username: string;
  role: string;
}

interface HeaderProps {
  user?: HeaderUser;
  onLogout?: () => void;
  menuOpen?: boolean;
  onMenuToggle?: () => void;
}

export function Header({ user, onLogout, menuOpen = false, onMenuToggle }: HeaderProps): JSX.Element {
  return (
    <header className="app-header">
      {onMenuToggle && (
        <button
          type="button"
          className="btn-icon app-header-menu"
          aria-expanded={menuOpen}
          aria-controls="primary-navigation"
          aria-label={menuOpen ? "Close navigation menu" : "Open navigation menu"}
          onClick={onMenuToggle}
        >
          <Icon name={menuOpen ? "close" : "menu"} />
        </button>
      )}

      <div className="app-header-brand">
        <img src="/helpdesk-pro-logo.png" alt="HelpDesk Pro" className="app-header-logo" />
        <span className="app-header-name">HelpDesk Pro</span>
      </div>

      {user && (
        <div className="app-header-user">
          <span className="avatar" aria-hidden="true">
            {user.username.slice(0, 1).toUpperCase()}
          </span>
          <span className="app-header-identity">
            <span className="app-header-username">{user.username}</span>
            <span className="app-header-role">{ROLE_LABEL[user.role] ?? user.role}</span>
          </span>
          {onLogout && (
            <button type="button" className="btn-secondary btn-sm app-header-logout" onClick={onLogout}>
              <Icon name="logout" size={16} />
              <span className="app-header-logout-text">Log out</span>
            </button>
          )}
        </div>
      )}
    </header>
  );
}
