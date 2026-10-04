// Rows with status, priority, SLA state badge (component-map.md:
// WorkbenchPage; E6-S1). Links to AgentTicketPage. Rows follow DESIGN.md
// 5.5: 56-64 px, hover tint, 3 px priority notch, truncating title.

import { Link } from "react-router-dom";

import type { QueueTicket, SlaState } from "../api/types";
import { EscalatedTag } from "./EscalatedTag";
import { PriorityBadge } from "./PriorityBadge";
import { SlaBadge } from "./SlaBadge";
import { StatusChip } from "./StatusChip";

const SLA_RANK: Record<SlaState, number> = { ON_TRACK: 0, AT_RISK: 1, BREACHED: 2 };

function worstSlaState(a: SlaState, b: SlaState): SlaState {
  return SLA_RANK[a] >= SLA_RANK[b] ? a : b;
}

interface TicketTableProps {
  tickets: QueueTicket[];
}

export function TicketTable({ tickets }: TicketTableProps): JSX.Element {
  return (
    <table className="data-table ticket-table">
      <thead>
        <tr>
          <th>Id</th>
          <th>Title</th>
          <th>Priority</th>
          <th>Status</th>
          <th>SLA state</th>
        </tr>
      </thead>
      <tbody>
        {tickets.map((ticket) => {
          const slaState = worstSlaState(ticket.response_state, ticket.resolution_state);
          return (
            <tr
              key={ticket.id}
              data-testid="queue-row"
              className={`ticket-row notch-${ticket.priority.toLowerCase()}`}
            >
              <td className="cell-id">
                <Link to={`/agent/tickets/${ticket.id}`} className="ticket-id">
                  {ticket.id}
                </Link>
              </td>
              <td className="cell-title">
                <span className="truncate">{ticket.title}</span>
                {ticket.escalated && <EscalatedTag />}
              </td>
              <td data-label="Priority">
                <PriorityBadge priority={ticket.priority} />
              </td>
              <td data-label="Status">
                <StatusChip status={ticket.status} />
              </td>
              <td data-label="SLA" data-testid="queue-row-sla-state">
                <SlaBadge state={slaState} />
              </td>
            </tr>
          );
        })}
      </tbody>
    </table>
  );
}
