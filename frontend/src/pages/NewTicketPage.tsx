// Confirmation shows the HD- id and status OPEN (component-map.md, E2-S4).

import { useState } from "react";

import { ApiError, apiRequest } from "../api/client";
import type { CreateTicketRequest, CreateTicketResponse } from "../api/types";
import { ErrorBanner } from "../components/ErrorBanner";
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
      <main>
        <h1>Ticket created</h1>
        <p>
          {confirmation.id} is {confirmation.status}.
        </p>
      </main>
    );
  }

  return (
    <main>
      <h1>New ticket</h1>
      <ErrorBanner message={error} />
      <TicketForm onSubmit={handleSubmit} />
    </main>
  );
}
