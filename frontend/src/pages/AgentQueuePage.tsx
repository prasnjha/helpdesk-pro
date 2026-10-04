// GET /api/agent/queues/{queue}/tickets with priority/status/escalated
// filters (component-map.md, E6-S1 AC-01/02). Rows link to TicketDetailPage,
// which carries the claim/reassign/status/note/reply/publish actions.

import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { ApiError, apiRequest } from "../api/client";
import type { Priority, QueueTicket, SlaState } from "../api/types";
import { ErrorBanner } from "../components/ErrorBanner";

const SLA_RANK: Record<SlaState, number> = { ON_TRACK: 0, AT_RISK: 1, BREACHED: 2 };

function worstSlaState(a: SlaState, b: SlaState): SlaState {
  return SLA_RANK[a] >= SLA_RANK[b] ? a : b;
}

const QUEUES = [
  { slug: "billing", name: "Billing" },
  { slug: "technical", name: "Technical" },
  { slug: "account", name: "Account" },
  { slug: "billing-tier-2", name: "Billing Tier 2" },
  { slug: "technical-tier-2", name: "Technical Tier 2" },
  { slug: "account-tier-2", name: "Account Tier 2" },
];

const PRIORITIES: Priority[] = ["Critical", "High", "Medium", "Low"];

export function AgentQueuePage(): JSX.Element {
  const [queue, setQueue] = useState(QUEUES[0].slug);
  const [priority, setPriority] = useState<Priority | "">("");
  const [tickets, setTickets] = useState<QueueTicket[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const params = new URLSearchParams();
    if (priority) params.set("priority", priority);
    const query = params.toString();
    apiRequest<QueueTicket[]>(`/api/agent/queues/${queue}/tickets${query ? `?${query}` : ""}`)
      .then(setTickets)
      .catch((err: unknown) => {
        setError(err instanceof ApiError ? err.message : "Unable to load the queue.");
      });
  }, [queue, priority]);

  return (
    <main>
      <h1>Agent workbench</h1>
      <ErrorBanner message={error} />

      <label htmlFor="queue-select">Queue</label>
      <select id="queue-select" value={queue} onChange={(e) => setQueue(e.target.value)}>
        {QUEUES.map((q) => (
          <option key={q.slug} value={q.slug}>
            {q.name}
          </option>
        ))}
      </select>

      <label htmlFor="priority-filter">Priority</label>
      <select
        id="priority-filter"
        value={priority}
        onChange={(e) => setPriority(e.target.value as Priority | "")}
      >
        <option value="">All</option>
        {PRIORITIES.map((p) => (
          <option key={p} value={p}>
            {p}
          </option>
        ))}
      </select>

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
                  <Link to={`/tickets/${ticket.id}`}>{ticket.id}</Link>
                </td>
                <td>{ticket.title}</td>
                <td>{ticket.priority}</td>
                <td>{ticket.status}</td>
                <td data-testid="queue-row-sla-state">{slaState}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </main>
  );
}
