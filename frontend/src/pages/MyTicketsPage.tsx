// GET /api/tickets, own tickets list (component-map.md, E2-S4).

import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { ApiError, apiRequest } from "../api/client";
import type { TicketSummary } from "../api/types";
import { ErrorBanner } from "../components/ErrorBanner";

export function MyTicketsPage(): JSX.Element {
  const [tickets, setTickets] = useState<TicketSummary[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiRequest<TicketSummary[]>("/api/tickets")
      .then(setTickets)
      .catch((err: unknown) => {
        setError(err instanceof ApiError ? err.message : "Unable to load tickets.");
      });
  }, []);

  return (
      <main>
      <h1>My tickets</h1>
      <ErrorBanner message={error} />
      <Link to="/tickets/new">New ticket</Link>
      <table>
        <thead>
          <tr>
            <th>Id</th>
            <th>Title</th>
            <th>Status</th>
            <th>Priority</th>
          </tr>
        </thead>
        <tbody>
          {tickets.map((ticket) => (
            <tr key={ticket.id}>
              <td>
                <Link to={`/tickets/${ticket.id}`}>{ticket.id}</Link>
              </td>
              <td>{ticket.title}</td>
              <td>{ticket.status}</td>
              <td>{ticket.priority}</td>
            </tr>
          ))}
        </tbody>
      </table>
      </main>
  );
}
