// Role-based primary navigation (DESIGN.md Section 5.6): a 240 px rail on
// desktop, an overlay drawer below 1024 px. Links only point at routes that
// already exist in App.tsx; AuthGuard still enforces access on each route.

import { Link, useLocation } from "react-router-dom";

import type { Role } from "../state/session";
import { Icon, type IconName } from "./Icon";

interface NavItem {
  label: string;
  to: string;
  icon: IconName;
  // Path prefixes that mark this item active, minus any excluded paths.
  match: string[];
  exclude?: string[];
}

const KB_ITEM: NavItem = {
  label: "Knowledge Base",
  to: "/kb",
  icon: "book",
  match: ["/kb", "/agent/kb"],
};

const NAV_BY_ROLE: Record<Role, NavItem[]> = {
  customer: [
    { label: "My tickets", to: "/tickets", icon: "ticket", match: ["/tickets"], exclude: ["/tickets/new"] },
    { label: "New ticket", to: "/tickets/new", icon: "plus", match: ["/tickets/new"] },
    KB_ITEM,
  ],
  agent: [
    {
      label: "Agent Queue",
      to: "/agent/queues/billing",
      icon: "inbox",
      match: ["/agent/queues", "/agent/tickets"],
    },
    KB_ITEM,
  ],
  admin: [
    { label: "Dashboard", to: "/admin/dashboard", icon: "chart", match: ["/admin/dashboard"] },
    { label: "SLA policies", to: "/admin/sla-policies", icon: "timer", match: ["/admin/sla-policies"] },
    KB_ITEM,
  ],
};

function startsWithSegment(pathname: string, prefix: string): boolean {
  return pathname === prefix || pathname.startsWith(`${prefix}/`);
}

function isActive(item: NavItem, pathname: string): boolean {
  if (item.exclude?.some((p) => startsWithSegment(pathname, p))) return false;
  return item.match.some((p) => startsWithSegment(pathname, p));
}

interface SideNavProps {
  role: Role | null;
  open: boolean;
  onNavigate: () => void;
}

export function SideNav({ role, open, onNavigate }: SideNavProps): JSX.Element {
  const { pathname } = useLocation();
  const items = role ? NAV_BY_ROLE[role] ?? [] : [];

  return (
    <nav
      id="primary-navigation"
      aria-label="Primary"
      className={open ? "side-nav is-open" : "side-nav"}
    >
      <p className="side-nav-heading">Workspace</p>
      <ul className="side-nav-list">
        {items.map((item) => {
          const active = isActive(item, pathname);
          return (
            <li key={item.to}>
              <Link
                to={item.to}
                className={active ? "side-nav-link is-active" : "side-nav-link"}
                aria-current={active ? "page" : undefined}
                onClick={onNavigate}
              >
                <Icon name={item.icon} />
                {item.label}
              </Link>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
