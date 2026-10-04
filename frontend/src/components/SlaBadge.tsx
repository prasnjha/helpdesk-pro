// Shows an SLA timer's state (component-map.md: TicketTable, AgentTicketPage,
// CustomerTicketPage; E6-S1, E3-S4). The text is the backend state verbatim
// (tests compare it exactly); colour follows DESIGN.md 1.3 — ON_TRACK the
// emerald Resolved row, AT_RISK the amber Warning row, BREACHED the rose
// Critical row (5.3: breach chips use the rose palette, not the red fill).

import type { SlaState } from "../api/types";

const SLA_CLASS: Record<SlaState, string> = {
  ON_TRACK: "chip-resolved",
  AT_RISK: "chip-warning",
  BREACHED: "chip-critical",
};

interface SlaBadgeProps {
  state: SlaState;
  testId?: string;
}

export function SlaBadge({ state, testId }: SlaBadgeProps): JSX.Element {
  return (
    <span className={`chip chip-dot ${SLA_CLASS[state]}`} data-testid={testId}>
      {state}
    </span>
  );
}
