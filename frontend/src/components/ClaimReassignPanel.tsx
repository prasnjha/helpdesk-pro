// Claim and reassign controls (component-map.md: AgentTicketPage; E6-S1).

import type { FormEvent } from "react";

interface ClaimReassignPanelProps {
  onClaim: () => void;
  reassignTo: string;
  onReassignToChange: (value: string) => void;
  onReassign: (event: FormEvent) => void;
}

export function ClaimReassignPanel({
  onClaim,
  reassignTo,
  onReassignToChange,
  onReassign,
}: ClaimReassignPanelProps): JSX.Element {
  return (
    <>
      <button type="button" onClick={onClaim}>
        Claim
      </button>

      <form onSubmit={onReassign}>
        <label htmlFor="reassign-to">Reassign to (user id)</label>
        <input
          id="reassign-to"
          value={reassignTo}
          onChange={(e) => onReassignToChange(e.target.value)}
        />
        <button type="submit">Reassign</button>
      </form>
    </>
  );
}
