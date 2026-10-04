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
      <button type="button" className="claim-button" onClick={onClaim}>
        Claim
      </button>

      <form onSubmit={onReassign} className="inline-form">
        <div className="field">
          <label htmlFor="reassign-to">Reassign to (user id)</label>
          <input
            id="reassign-to"
            value={reassignTo}
            placeholder="e.g. AG-2"
            onChange={(e) => onReassignToChange(e.target.value)}
          />
        </div>
        <button type="submit" className="btn-secondary">
          Reassign
        </button>
      </form>
    </>
  );
}
