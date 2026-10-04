// Ticket detail header card shared by CustomerTicketPage and AgentTicketPage
// (ticket-detail-active.png / ticket-detail-customer-view.png): id, status,
// priority and escalated chips, the title, the description, and a meta strip.
// Presentational only. Test ids are the ones the pages always exposed.

import type { ReactNode } from "react";

import type { TicketDetail } from "../api/types";
import { formatDate } from "../utils/format";
import { EscalatedTag } from "./EscalatedTag";
import { PriorityBadge } from "./PriorityBadge";
import { StatusChip } from "./StatusChip";

interface TicketHeaderProps {
  ticket: TicketDetail;
  aside?: ReactNode;
}

export function TicketHeader({ ticket, aside }: TicketHeaderProps): JSX.Element {
  return (
    <div className="card ticket-header">
      <div className="ticket-header-top">
        <dl className="ticket-chips">
          <div>
            <dt className="sr-only">Id</dt>
            <dd className="code-chip">{ticket.id}</dd>
          </div>
          <div>
            <dt className="sr-only">Status</dt>
            <dd data-testid="ticket-status">
              <StatusChip status={ticket.status} />
            </dd>
          </div>
          <div>
            <dt className="sr-only">Priority</dt>
            <dd>
              <PriorityBadge priority={ticket.priority} />
            </dd>
          </div>
          {ticket.escalated && (
            <div>
              <dd data-testid="ticket-escalated">
                <EscalatedTag />
              </dd>
            </div>
          )}
        </dl>
        {aside}
      </div>

      <h1 className="ticket-title">{ticket.title}</h1>
      <p className="ticket-description">{ticket.description}</p>

      <dl className="ticket-meta">
        <div>
          <dt>Assignee</dt>
          <dd data-testid="ticket-assignee">{ticket.assignee_id ?? "Unassigned"}</dd>
        </div>
        <div>
          <dt>Queue</dt>
          <dd>{ticket.queue.name}</dd>
        </div>
        <div>
          <dt>Category</dt>
          <dd>{ticket.category}</dd>
        </div>
        <div>
          <dt>Opened</dt>
          <dd>{formatDate(ticket.created_at)}</dd>
        </div>
      </dl>
    </div>
  );
}
