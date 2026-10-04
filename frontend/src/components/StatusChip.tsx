// Ticket status pill (DESIGN.md 1.3 / 5.3). The text is the backend status
// enum verbatim; only the colour changes. OPEN uses the Open/Triage row,
// IN_PROGRESS the In-progress/Warning row, RESOLVED the Resolved row.
// PENDING_CUSTOMER and CLOSED have no row of their own, so they use neutral
// slate surfaces (DESIGN.md 5.7: blue is for interaction, red only for
// breaches) — pending is lighter, closed is the muted terminal state.

const STATUS_CLASS: Record<string, string> = {
  OPEN: "chip-open",
  IN_PROGRESS: "chip-warning",
  PENDING_CUSTOMER: "chip-pending",
  RESOLVED: "chip-resolved",
  CLOSED: "chip-closed",
};

interface StatusChipProps {
  status: string;
  testId?: string;
}

export function StatusChip({ status, testId }: StatusChipProps): JSX.Element {
  return (
    <span className={`chip ${STATUS_CLASS[status] ?? "chip-closed"}`} data-testid={testId}>
      {status}
    </span>
  );
}
