// Confirmation shows the HD- id and status OPEN (component-map.md, E2-S4).
// Laid out after new-ticket.png: back link, title + lead, the form in a
// card; the confirmation is a success card.

import { useState } from "react";
import { Link } from "react-router-dom";

import { ApiError, apiRequest } from "../api/client";
import type { CreateTicketRequest, CreateTicketResponse } from "../api/types";
import { BackLink } from "../components/BackLink";
import { ErrorBanner } from "../components/ErrorBanner";
import { Icon } from "../components/Icon";
import { TicketForm } from "../components/TicketForm";

export function NewTicketPage(): JSX.Element {
  const [confirmation, setConfirmation] = useState<CreateTicketResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(payload: CreateTicketRequest): Promise<void> {
    setError(null);
    try {
      const response = await apiRequest<CreateTicketResponse>("/api/tickets", {
        method: "POST",
        body: payload,
      });
      setConfirmation(response);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Unable to create the ticket.");
    }
  }

  if (confirmation) {
    return (
      <main className="page-narrow">
        <div className="card confirmation-card">
          <span className="confirmation-icon">
            <Icon name="check" size={28} />
          </span>
          <h1>Ticket created</h1>
          <p className="confirmation-text">
            {confirmation.id} is {confirmation.status}.
          </p>
          <Link to="/tickets" className="btn btn-secondary">
            Back to my tickets
          </Link>
        </div>
      </main>
    );
  }

  return (
    <main className="page-narrow">
      <BackLink to="/tickets">Back to my tickets</BackLink>
      <div className="page-heading">
        <h1>New ticket</h1>
        <p className="page-lead">Submit a support request or report a problem.</p>
      </div>
      <ErrorBanner message={error} />
      <div className="card">
        <TicketForm onSubmit={handleSubmit} />
      </div>
    </main>
  );
}
