// GET /api/tickets/{id} and the lifecycle/claim/reassign/notes/replies actions
// (component-map.md, E6-S1, E6-S3, AC-03/04/07/08). Shared by customer,
// agent and admin: the backend already filters notes/history to agent/admin
// only, so this page shows action controls when the viewer's role allows
// them and never shows notes/history for a customer.

import { useCallback, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { ApiError, apiRequest } from "../api/client";
import type {
  AssignmentResponse,
  NoteResponse,
  ReplyResponse,
  SlaSnapshot,
  Status,
  StatusResponse,
  TicketDetail,
} from "../api/types";
import { ErrorBanner } from "../components/ErrorBanner";
import { getRole } from "../state/session";

const STATUS_OPTIONS: Status[] = ["OPEN", "IN_PROGRESS", "PENDING_CUSTOMER", "RESOLVED", "CLOSED"];

export function TicketDetailPage(): JSX.Element {
  const { id } = useParams<{ id: string }>();
  const role = getRole();
  const isStaff = role === "agent" || role === "admin";

  const [ticket, setTicket] = useState<TicketDetail | null>(null);
  const [sla, setSla] = useState<SlaSnapshot | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [replyBody, setReplyBody] = useState("");
  const [noteBody, setNoteBody] = useState("");
  const [reassignTo, setReassignTo] = useState("");
  const [nextStatus, setNextStatus] = useState<Status>("IN_PROGRESS");

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

  async function runAction<T>(action: () => Promise<T>): Promise<void> {
    setError(null);
    try {
      await action();
      load(); // re-fetch in place — no page reload (E6-S1 AC-03).
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "The action could not be completed.");
    }
  }

  function handleClaim(): void {
    if (!ticket) return;
    void runAction(() =>
      apiRequest<AssignmentResponse>(`/api/tickets/${ticket.id}/claim`, {
        method: "POST",
        body: { version: ticket.version },
      })
    );
  }

  function handleReassign(event: React.FormEvent): void {
    event.preventDefault();
    if (!ticket || reassignTo.trim().length === 0) return;
    void runAction(() =>
      apiRequest<AssignmentResponse>(`/api/tickets/${ticket.id}/reassign`, {
        method: "POST",
        body: { assignee_id: reassignTo, version: ticket.version },
      })
    ).then(() => setReassignTo(""));
  }

  function handleStatusChange(event: React.FormEvent): void {
    event.preventDefault();
    if (!ticket) return;
    void runAction(() =>
      apiRequest<StatusResponse>(`/api/tickets/${ticket.id}/status`, {
        method: "POST",
        body: { to_status: nextStatus, version: ticket.version },
      })
    );
  }

  function handleAddNote(event: React.FormEvent): void {
    event.preventDefault();
    if (!ticket || noteBody.trim().length === 0) return;
    void runAction(() =>
      apiRequest<NoteResponse>(`/api/tickets/${ticket.id}/notes`, {
        method: "POST",
        body: { body: noteBody },
      })
    ).then(() => setNoteBody(""));
  }

  function handleReply(event: React.FormEvent): void {
    event.preventDefault();
    if (!ticket || replyBody.trim().length === 0) return;
    void runAction(() =>
      apiRequest<ReplyResponse>(`/api/tickets/${ticket.id}/replies`, {
        method: "POST",
        body: { body: replyBody },
      })
    ).then(() => setReplyBody(""));
  }

  if (!ticket) {
    return (
      <main>
        <ErrorBanner message={error} />
      </main>
    );
  }

  const canReply = ticket.status !== "RESOLVED" && ticket.status !== "CLOSED";
  const canPublishToKb = ticket.status === "RESOLVED" || ticket.status === "CLOSED";

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
          <p data-testid="sla-response-state">Response: {sla.response.state}</p>
          <p data-testid="sla-resolution-state">Resolution: {sla.resolution.state}</p>
        </section>
      )}

      {isStaff && (
        <section aria-label="Agent actions">
          <h2>Actions</h2>
          <button type="button" onClick={handleClaim}>
            Claim
          </button>

          <form onSubmit={handleReassign}>
            <label htmlFor="reassign-to">Reassign to (user id)</label>
            <input
              id="reassign-to"
              value={reassignTo}
              onChange={(e) => setReassignTo(e.target.value)}
            />
            <button type="submit">Reassign</button>
          </form>

          <form onSubmit={handleStatusChange}>
            <label htmlFor="next-status">Change status</label>
            <select
              id="next-status"
              value={nextStatus}
              onChange={(e) => setNextStatus(e.target.value as Status)}
            >
              {STATUS_OPTIONS.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </select>
            <button type="submit">Update status</button>
          </form>

          {canPublishToKb && (
            <Link to={`/kb/new?source_ticket_id=${ticket.id}`}>Publish to knowledge base</Link>
          )}
        </section>
      )}

      {isStaff && (
        <section aria-label="Internal notes">
          <h2>Internal notes</h2>
          <ul>
            {ticket.notes.map((note) => (
              <li key={note.id}>{note.body}</li>
            ))}
          </ul>
          <form onSubmit={handleAddNote}>
            <label htmlFor="note-body">Add a note</label>
            <textarea id="note-body" value={noteBody} onChange={(e) => setNoteBody(e.target.value)} />
            <button type="submit">Add note</button>
          </form>
        </section>
      )}

      <section aria-label="Replies">
        <h2>Replies</h2>
        <ul>
          {ticket.replies.map((reply) => (
            <li key={reply.id}>
              <strong>{reply.author_role}:</strong> {reply.body}
            </li>
          ))}
        </ul>
        {canReply && (
          <form onSubmit={handleReply} aria-label="Reply box">
            <label htmlFor="reply-body">Reply</label>
            <textarea
              id="reply-body"
              value={replyBody}
              onChange={(e) => setReplyBody(e.target.value)}
            />
            <button type="submit">Send reply</button>
          </form>
        )}
      </section>

      {isStaff && (
        <section aria-label="History">
          <h2>History</h2>
          <ul>
            {ticket.history.map((entry) => (
              <li key={entry.id}>
                {entry.event}: {entry.from_state ?? "—"} to {entry.to_state ?? "—"}
              </li>
            ))}
          </ul>
        </section>
      )}
    </main>
  );
}
