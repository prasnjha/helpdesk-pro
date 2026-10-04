// The escalated flag (ticket.escalated) as an uppercase rose tag
// (agent-ticket-queue.png / ticket-detail-active.png "ESCALATED").

import { Icon } from "./Icon";

interface EscalatedTagProps {
  testId?: string;
}

export function EscalatedTag({ testId }: EscalatedTagProps): JSX.Element {
  return (
    <span className="chip tag-escalated" data-testid={testId}>
      <Icon name="flag" size={12} />
      Escalated
    </span>
  );
}
