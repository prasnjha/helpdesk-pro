// GET /api/tickets/{id}, GET /api/tickets/{id}/sla, and the lifecycle/claim/
// reassign/notes/replies actions (component-map.md, E6-S1, AC-03/04/07/08).
// Agent-initiated edges only (ticket-lifecycle_spec.md Section 2); the
// customer-initiated PENDING_CUSTOMER -> OPEN edge happens via a reply on
// CustomerTicketPage, not this control, and CLOSED is terminal.

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
import { ClaimReassignPanel } from "../components/ClaimReassignPanel";
import { ErrorBanner } from "../components/ErrorBanner";
import { ReplyBox } from "../components/ReplyBox";
import { SlaBadge } from "../components/SlaBadge";
import { StatusControl } from "../components/StatusControl";
import { ThreadPanel } from "../components/ThreadPanel";

const VALID_NEXT_STATES: Record<Status, Status[]> = {
  OPEN: ["IN_PROGRESS"],
  IN_PROGRESS: ["PENDING_CUSTOMER", "RESOLVED"],
  PENDING_CUSTOMER: ["RESOLVED"],
  RESOLVED: ["CLOSED"],
  CLOSED: [],
};

export function AgentTicketPage(): JSX.Element {
  const { id } = useParams<{ id: string }>();

  const [ticket, setTicket] = useState<TicketDetail | null>(null);
  const [sla, setSla] = useState<SlaSnapshot | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [replyBody, setReplyBody] = useState("");
  const [noteBody, setNoteBody] = useState("");
  const [reassignTo, setReassignTo] = useState("");
  const [nextStatus, setNextStatus] = useState<Status | "">("");

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
    const toStatus = nextStatus === "" ? VALID_NEXT_STATES[ticket?.status ?? "CLOSED"][0] : nextStatus;
    if (!ticket || !toStatus) return;
    void runAction(() =>
      apiRequest<StatusResponse>(`/api/tickets/${ticket.id}/status`, {
        method: "POST",
        body: { to_status: toStatus, version: ticket.version },
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
  const isClosed = ticket.status === "CLOSED";
  const nextStates = VALID_NEXT_STATES[ticket.status];
  const selectedNextStatus = nextStatus === "" ? nextStates[0] ?? "" : nextStatus;

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

      {isClosed && <p>Closed tickets cannot be changed.</p>}

      {!isClosed && (
        <section aria-label="Agent actions">
          <h2>Actions</h2>
          <ClaimReassignPanel
            onClaim={handleClaim}
            reassignTo={reassignTo}
            onReassignToChange={setReassignTo}
            onReassign={handleReassign}
          />
          <StatusControl
            nextStates={nextStates}
            selected={selectedNextStatus}
            onChange={setNextStatus}
            onSubmit={handleStatusChange}
          />
        </section>
      )}

      {canPublishToKb && (
        <Link to={`/agent/kb/new?source_ticket_id=${ticket.id}`}>Publish to knowledge base</Link>
      )}

      <ThreadPanel
        replies={ticket.replies}
        notes={ticket.notes}
        showNotes
        noteForm={
          !isClosed ? (
            <form onSubmit={handleAddNote}>
              <label htmlFor="note-body">Add a note</label>
              <textarea id="note-body" value={noteBody} onChange={(e) => setNoteBody(e.target.value)} />
              <button type="submit">Add note</button>
            </form>
          ) : null
        }
        replyBox={
          canReply ? <ReplyBox value={replyBody} onChange={setReplyBody} onSubmit={handleReply} /> : null
        }
      />

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
    </main>
  );
}
