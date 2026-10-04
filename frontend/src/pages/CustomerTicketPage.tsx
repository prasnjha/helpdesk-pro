// GET /api/tickets/{id}, GET /api/tickets/{id}/sla, POST
// /api/tickets/{id}/replies (component-map.md, E3-S4, E6-S3, AC-08). The
// backend already filters notes/history to agent/admin only, so this page
// never renders them.

import { useCallback, useEffect, useState } from "react";
import { useParams } from "react-router-dom";

import { ApiError, apiRequest } from "../api/client";
import type { ReplyResponse, SlaSnapshot, TicketDetail } from "../api/types";
import { ErrorBanner } from "../components/ErrorBanner";
import { ReplyBox } from "../components/ReplyBox";
import { SlaBadge } from "../components/SlaBadge";
import { ThreadPanel } from "../components/ThreadPanel";

export function CustomerTicketPage(): JSX.Element {
  const { id } = useParams<{ id: string }>();

  const [ticket, setTicket] = useState<TicketDetail | null>(null);
  const [sla, setSla] = useState<SlaSnapshot | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [replyBody, setReplyBody] = useState("");

  const load = useCallback(() => {
    if (!id) return;
    apiRequest<TicketDetail>(`/api/tickets/${id}`)
      .then(setTicket)
      .catch((err: unknown) => {
        setError(err instanceof ApiError ? err.message : "Unable to load this ticket.");
      });
    apiRequest<SlaSnapshot>(`/api/tickets/${id}/sla`)
      .then(setSla)
      .catch(() => {
        // SLA snapshot is supplementary; the main detail load already reports errors.
      });
  }, [id]);

  useEffect(() => {
    load();
  }, [load]);

  function handleReply(event: React.FormEvent): void {
    event.preventDefault();
    if (!ticket || replyBody.trim().length === 0) return;
    setError(null);
    apiRequest<ReplyResponse>(`/api/tickets/${ticket.id}/replies`, {
      method: "POST",
      body: { body: replyBody },
    })
      .then(() => {
        setReplyBody("");
        load();
      })
      .catch((err: unknown) => {
        setError(err instanceof ApiError ? err.message : "The action could not be completed.");
      });
  }

  if (!ticket) {
    return (
      <main>
        <ErrorBanner message={error} />
      </main>
    );
  }

  const canReply = ticket.status !== "RESOLVED" && ticket.status !== "CLOSED";

  return (
    <main>
      <h1>{ticket.title}</h1>
      <ErrorBanner message={error} />
      <dl>
        <dt>Id</dt>
        <dd>{ticket.id}</dd>
        <dt>Status</dt>
        <dd data-testid="ticket-status">{ticket.status}</dd>
        <dt>Priority</dt>
        <dd>{ticket.priority}</dd>
        <dt>Assignee</dt>
        <dd data-testid="ticket-assignee">{ticket.assignee_id ?? "Unassigned"}</dd>
        {ticket.escalated && <dd data-testid="ticket-escalated">Escalated</dd>}
      </dl>
      <p>{ticket.description}</p>

      {sla && (
        <section aria-label="SLA status">
          <p data-testid="sla-response-state">
            Response: <SlaBadge state={sla.response.state} />
          </p>
          <p data-testid="sla-resolution-state">
            Resolution: <SlaBadge state={sla.resolution.state} />
          </p>
        </section>
      )}

      <ThreadPanel
        replies={ticket.replies}
        notes={[]}
        showNotes={false}
        replyBox={
          canReply ? <ReplyBox value={replyBody} onChange={setReplyBody} onSubmit={handleReply} /> : null
        }
      />
    </main>
  );
}
