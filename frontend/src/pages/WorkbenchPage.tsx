// GET /api/agent/queues/{queue}/tickets with priority/status/escalated
// filters (component-map.md, E6-S1 AC-01/02). Rows link to AgentTicketPage,
// which carries the claim/reassign/status/note/reply/publish actions.

import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { ApiError, apiRequest } from "../api/client";
import type { Priority, QueueRef, QueueTicket } from "../api/types";
import { ErrorBanner } from "../components/ErrorBanner";
import { Icon } from "../components/Icon";
import { QueueFilters } from "../components/QueueFilters";
import { TicketTable } from "../components/TicketTable";

const QUEUES: QueueRef[] = [
  { slug: "billing", name: "Billing" },
  { slug: "technical", name: "Technical" },
  { slug: "account", name: "Account" },
  { slug: "billing-tier-2", name: "Billing Tier 2" },
  { slug: "technical-tier-2", name: "Technical Tier 2" },
  { slug: "account-tier-2", name: "Account Tier 2" },
];

const PRIORITIES: Priority[] = ["Critical", "High", "Medium", "Low"];

export function WorkbenchPage(): JSX.Element {
  const { queue: queueParam } = useParams<{ queue: string }>();
  const navigate = useNavigate();
  const queue = queueParam ?? QUEUES[0].slug;
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

  function handleQueueChange(nextQueue: string): void {
    navigate(`/agent/queues/${nextQueue}`);
  }

  return (
    <main className="page-wide">
      <div className="page-header">
        <div className="page-title-group">
          <h1>Agent workbench</h1>
          <span className="count-pill">
            {tickets.length} {tickets.length === 1 ? "ticket" : "tickets"}
          </span>
        </div>
      </div>
      <ErrorBanner message={error} />

      <div className="workbench-layout">
        <aside className="card workbench-filters">
          <h2 className="card-title">
            <Icon name="filter" />
            Filters
          </h2>
          <QueueFilters
            queue={queue}
            queues={QUEUES}
            onQueueChange={handleQueueChange}
            priority={priority}
            priorities={PRIORITIES}
            onPriorityChange={setPriority}
          />
        </aside>

        <div className="card table-card">
          <TicketTable tickets={tickets} />
          {tickets.length === 0 && <p className="table-empty">No tickets in this queue.</p>}
        </div>
      </div>
    </main>
  );
}
