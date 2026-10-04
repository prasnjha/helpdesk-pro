// GET /api/tickets, own tickets list (component-map.md, E2-S4). Laid out
// after my-tickets.png: title with a count pill, then one card per ticket
// (id, status chip, priority, truncating title, updated date and category).

import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { ApiError, apiRequest } from "../api/client";
import type { TicketSummary } from "../api/types";
import { ErrorBanner } from "../components/ErrorBanner";
import { Icon } from "../components/Icon";
import { PriorityBadge } from "../components/PriorityBadge";
import { StatusChip } from "../components/StatusChip";
import { formatDate } from "../utils/format";

// One ticket as a card. The id link stretches over the whole card (CSS) so
// the card is clickable, while its accessible name stays the ticket id.
function TicketCard({ ticket }: { ticket: TicketSummary }): JSX.Element {
  return (
    <li className={`card ticket-card notch-card notch-${ticket.priority.toLowerCase()}`}>
      <div className="ticket-card-top">
        <Link to={`/tickets/${ticket.id}`} className="ticket-id ticket-card-link">
          {ticket.id}
        </Link>
        <StatusChip status={ticket.status} />
        <PriorityBadge priority={ticket.priority} />
      </div>
      <p className="ticket-card-title truncate">{ticket.title}</p>
      <p className="ticket-card-meta">
        <Icon name="clock" size={16} />
        Updated {formatDate(ticket.updated_at)}
        <span aria-hidden="true">•</span>
        {ticket.category}
      </p>
      <Icon name="chevronRight" className="ticket-card-chevron" />
    </li>
  );
}

export function MyTicketsPage(): JSX.Element {
  const [tickets, setTickets] = useState<TicketSummary[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    apiRequest<TicketSummary[]>("/api/tickets")
      .then(setTickets)
      .catch((err: unknown) => {
        setError(err instanceof ApiError ? err.message : "Unable to load tickets.");
      })
      .finally(() => setLoaded(true));
  }, []);

  return (
    <main>
      <div className="page-header">
        <div className="page-title-group">
          <h1>My tickets</h1>
          {loaded && (
            <span className="count-pill">
              {tickets.length} {tickets.length === 1 ? "ticket" : "tickets"}
            </span>
          )}
        </div>
        {/* Shown only while the sidebar is collapsed (< 1024 px); on desktop
            the sidebar's "New ticket" link is the single entry point. */}
        <Link to="/tickets/new" className="btn page-header-cta-mobile">
          <Icon name="plus" size={18} />
          New ticket
        </Link>
      </div>
      <ErrorBanner message={error} />

      <ul className="ticket-card-list" aria-label="Your tickets">
        {tickets.map((ticket) => (
          <TicketCard key={ticket.id} ticket={ticket} />
        ))}
      </ul>
      {loaded && tickets.length === 0 && !error && (
        <div className="card empty-state">
          <p>You have no tickets yet.</p>
        </div>
      )}
    </main>
  );
}
