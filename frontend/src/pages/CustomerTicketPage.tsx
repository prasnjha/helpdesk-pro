// GET /api/tickets/{id}, GET /api/tickets/{id}/sla, POST
// /api/tickets/{id}/replies (component-map.md, E3-S4, E6-S3, AC-08). The
// backend already filters notes/history to agent/admin only, so this page
// never renders them. Laid out after ticket-detail-customer-view.png.

import { useCallback, useEffect, useState } from "react";
import { useParams } from "react-router-dom";

import { ApiError, apiRequest } from "../api/client";
import type { ReplyResponse, SlaSnapshot, TicketDetail } from "../api/types";
import { BackLink } from "../components/BackLink";
import { ErrorBanner } from "../components/ErrorBanner";
import { Icon } from "../components/Icon";
import { ReplyBox } from "../components/ReplyBox";
import { SlaPanel } from "../components/SlaPanel";
import { ThreadPanel } from "../components/ThreadPanel";
import { TicketHeader } from "../components/TicketHeader";

// Presentational hint shown while the ticket waits on the customer
// (ticket-detail-customer-view.png "We're waiting for your reply").
function AwaitingReplyBanner(): JSX.Element {
  return (
    <div className="banner banner-info">
      <Icon name="alert" />
      <div className="banner-body">
        <strong>We&apos;re waiting for your reply</strong>
        <p>The support team asked for more details. Your response keeps this ticket moving.</p>
      </div>
    </div>
  );
}

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
        <BackLink to="/tickets">Back to my tickets</BackLink>
        <ErrorBanner message={error} />
      </main>
    );
  }

  const canReply = ticket.status !== "RESOLVED" && ticket.status !== "CLOSED";

  return (
    <main>
      <BackLink to="/tickets">Back to my tickets</BackLink>
      <ErrorBanner message={error} />
      <TicketHeader ticket={ticket} />
      {ticket.status === "PENDING_CUSTOMER" && <AwaitingReplyBanner />}

      <div className="detail-layout">
        <div className="detail-main">
          <ThreadPanel
            replies={ticket.replies}
            notes={[]}
            showNotes={false}
            replyBox={
              canReply ? <ReplyBox value={replyBody} onChange={setReplyBody} onSubmit={handleReply} /> : null
            }
          />
        </div>
        <aside className="detail-side">{sla && <SlaPanel sla={sla} />}</aside>
      </div>
    </main>
  );
}
