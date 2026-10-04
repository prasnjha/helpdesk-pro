// "← Back to …" link at the top of detail pages (mockups: new-ticket.png,
// ticket-detail-*.png, article-detail-*.png). Points at an existing route.

import type { ReactNode } from "react";
import { Link } from "react-router-dom";

import { Icon } from "./Icon";

interface BackLinkProps {
  to: string;
  children: ReactNode;
}

export function BackLink({ to, children }: BackLinkProps): JSX.Element {
  return (
    <Link to={to} className="back-link">
      <Icon name="arrowLeft" size={18} />
      {children}
    </Link>
  );
}
