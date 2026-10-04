// Shared admin console heading (admin-console.png): eyebrow, the
// "Admin console" title and a one-line lead for the current admin screen.

import { Icon } from "./Icon";

interface AdminPageHeadingProps {
  lead: string;
}

export function AdminPageHeading({ lead }: AdminPageHeadingProps): JSX.Element {
  return (
    <div className="page-heading">
      <p className="eyebrow">
        <Icon name="timer" size={16} />
        System administration
      </p>
      <h1>Admin console</h1>
      <p className="page-lead">{lead}</p>
    </div>
  );
}
