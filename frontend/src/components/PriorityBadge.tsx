// Priority label with a leading urgency dot (mockups: my-tickets.png,
// agent-ticket-queue.png). Critical takes the critical red; High the
// approaching-SLA amber; Medium and Low stay neutral (DESIGN.md 5.7).

import type { Priority } from "../api/types";

interface PriorityBadgeProps {
  priority: Priority;
}

export function PriorityBadge({ priority }: PriorityBadgeProps): JSX.Element {
  return <span className={`priority priority-${priority.toLowerCase()}`}>{priority}</span>;
}
