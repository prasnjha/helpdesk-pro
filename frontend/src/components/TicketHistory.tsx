// Append-only ticket history as a timeline card (ticket-detail-active.png
// "Status History"). History rows and assignment rows (claims and reassigns)
// are merged and shown oldest first. Staff only: AgentTicketPage renders it;
// the customer page never does (the backend filters both lists for customers).

import type { TicketAssignmentEntry, TicketHistoryEntry } from "../api/types";
import { formatDateTime, parse } from "../utils/format";
import { Icon } from "./Icon";

interface TicketHistoryProps {
  history: TicketHistoryEntry[];
  assignments: TicketAssignmentEntry[];
}

interface TimelineEntry {
  key: string;
  createdAt: string;
  event: string;
  actorId: string;
}

// Print only the states that exist. A missing state is never shown as a dash.
function historyEventLabel(entry: TicketHistoryEntry): string {
  const { event, from_state: from, to_state: to } = entry;
  if (from && to) return `${event}: ${from} to ${to}`;
  if (to) return `${event}: to ${to}`;
  if (from) return `${event}: from ${from}`;
  return event;
}

function assignmentEventLabel(entry: TicketAssignmentEntry): string {
  if (entry.from_user_id === null) {
    // A claim names the assignee, which is also the actor. Other assignments
    // name only the new assignee; the actor is on the meta line.
    return entry.actor_id === entry.to_user_id
      ? `ASSIGNED: ${entry.to_user_id} claimed`
      : `ASSIGNED: to ${entry.to_user_id}`;
  }
  return `REASSIGNED: ${entry.from_user_id} to ${entry.to_user_id}`;
}

// An unparseable timestamp sorts first, so the order stays defined.
function timeOf(value: string): number {
  return parse(value)?.getTime() ?? 0;
}

function timelineEntries(
  history: TicketHistoryEntry[],
  assignments: TicketAssignmentEntry[]
): TimelineEntry[] {
  const entries: TimelineEntry[] = [
    ...history.map((h) => ({
      key: `history-${h.id}`,
      createdAt: h.created_at,
      event: historyEventLabel(h),
      actorId: h.actor_id,
    })),
    ...assignments.map((a) => ({
      key: `assignment-${a.id}`,
      createdAt: a.created_at,
      event: assignmentEventLabel(a),
      actorId: a.actor_id,
    })),
  ];
  return entries.sort((a, b) => timeOf(a.createdAt) - timeOf(b.createdAt));
}

export function TicketHistory({ history, assignments }: TicketHistoryProps): JSX.Element {
  const entries = timelineEntries(history, assignments);
  return (
    <section aria-label="History" className="card">
      <div className="card-header">
        <h2 className="card-title">
          <Icon name="history" />
          History
        </h2>
      </div>
      <ol className="timeline">
        {entries.map((entry) => (
          <li key={entry.key} className="timeline-item">
            <span className="timeline-dot" aria-hidden="true" />
            <div className="timeline-body">
              <p className="timeline-event">{entry.event}</p>
              <p className="timeline-meta">
                {entry.actorId} · {formatDateTime(entry.createdAt)}
              </p>
            </div>
          </li>
        ))}
      </ol>
      {entries.length === 0 && <p className="muted-text">No history yet.</p>}
    </section>
  );
}
