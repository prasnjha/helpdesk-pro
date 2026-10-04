// Rows with status, priority, SLA state badge (component-map.md:
// WorkbenchPage; E6-S1). Links to AgentTicketPage.

import { Link } from "react-router-dom";

import type { QueueTicket, SlaState } from "../api/types";
import { SlaBadge } from "./SlaBadge";

const SLA_RANK: Record<SlaState, number> = { ON_TRACK: 0, AT_RISK: 1, BREACHED: 2 };

function worstSlaState(a: SlaState, b: SlaState): SlaState {
  return SLA_RANK[a] >= SLA_RANK[b] ? a : b;
}

interface TicketTableProps {
  tickets: QueueTicket[];
}

export function TicketTable({ tickets }: TicketTableProps): JSX.Element {
  return (
    <table>
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
            <tr key={ticket.id} data-testid="queue-row">
              <td>
                <Link to={`/agent/tickets/${ticket.id}`}>{ticket.id}</Link>
              </td>
              <td>{ticket.title}</td>
              <td>{ticket.priority}</td>
              <td>{ticket.status}</td>
              <td data-testid="queue-row-sla-state">
                <SlaBadge state={slaState} />
              </td>
            </tr>
          );
        })}
      </tbody>
    </table>
  );
}
