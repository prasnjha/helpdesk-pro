// Append-only ticket history as a timeline card (ticket-detail-active.png
// "Status History"). Staff only: AgentTicketPage renders it; the customer
// page never does (the backend filters history for customers anyway).

import type { TicketHistoryEntry } from "../api/types";
import { formatDateTime } from "../utils/format";
import { Icon } from "./Icon";

interface TicketHistoryProps {
  history: TicketHistoryEntry[];
}

export function TicketHistory({ history }: TicketHistoryProps): JSX.Element {
  return (
    <section aria-label="History" className="card">
      <div className="card-header">
        <h2 className="card-title">
          <Icon name="history" />
          History
        </h2>
      </div>
      <ol className="timeline">
        {history.map((entry) => (
          <li key={entry.id} className="timeline-item">
            <span className="timeline-dot" aria-hidden="true" />
            <div className="timeline-body">
              <p className="timeline-event">
                {entry.event}: {entry.from_state ?? "—"} to {entry.to_state ?? "—"}
              </p>
              <p className="timeline-meta">
                {entry.actor_id} · {formatDateTime(entry.created_at)}
              </p>
            </div>
          </li>
        ))}
      </ol>
      {history.length === 0 && <p className="muted-text">No history yet.</p>}
    </section>
  );
}
