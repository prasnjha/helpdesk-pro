// Shows an SLA timer's state (component-map.md: TicketTable, AgentTicketPage,
// CustomerTicketPage; E6-S1, E3-S4).

import type { SlaState } from "../api/types";

interface SlaBadgeProps {
  state: SlaState;
  testId?: string;
}

export function SlaBadge({ state, testId }: SlaBadgeProps): JSX.Element {
  return <span data-testid={testId}>{state}</span>;
}
