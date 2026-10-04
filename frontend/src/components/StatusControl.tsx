// Offers only the valid next states; a 409 surfaces through ErrorBanner at
// the page level (component-map.md: AgentTicketPage; E6-S1).

import type { FormEvent } from "react";

import type { Status } from "../api/types";

interface StatusControlProps {
  nextStates: Status[];
  selected: Status | "";
  onChange: (value: Status) => void;
  onSubmit: (event: FormEvent) => void;
}

export function StatusControl({
  nextStates,
  selected,
  onChange,
  onSubmit,
}: StatusControlProps): JSX.Element | null {
  if (nextStates.length === 0) return null;
  return (
    <form onSubmit={onSubmit} className="inline-form">
      <div className="field">
        <label htmlFor="next-status">Change status</label>
        <select id="next-status" value={selected} onChange={(e) => onChange(e.target.value as Status)}>
          {nextStates.map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </select>
      </div>
      <button type="submit">Update status</button>
    </form>
  );
}
