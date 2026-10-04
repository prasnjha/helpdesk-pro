import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { clearSession, setSession } from "../state/session";
import { CustomerTicketPage } from "./CustomerTicketPage";

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), { status });
}

const baseTicket = {
  id: "HD-000001",
  title: "Invoice issue",
  description: "Billed twice",
  category: "Billing",
  priority: "High",
  status: "PENDING_CUSTOMER",
  queue: { slug: "billing", name: "Billing" },
  customer_id: "C-1",
  assignee_id: "AG-1",
  escalated: false,
  version: 1,
  sla_policy_version_id: 1,
  created_at: "2026-01-01T00:00:00Z",
  updated_at: "2026-01-01T00:00:00Z",
  replies: [],
  notes: [],
  history: [],
};

const slaSnapshot = {
  response: { target_minutes: 60, elapsed_minutes: 5, state: "ON_TRACK", stopped_at: null },
  resolution: { target_minutes: 480, elapsed_minutes: 5, state: "ON_TRACK", stopped_at: null },
};

function renderPage(): void {
  render(
    <MemoryRouter initialEntries={["/tickets/HD-000001"]}>
      <Routes>
        <Route path="/tickets/:id" element={<CustomerTicketPage />} />
      </Routes>
    </MemoryRouter>
  );
}

describe("CustomerTicketPage", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
    setSession("tok", "customer", "customer1");
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    clearSession();
  });

  it("E6S3_customer_sees_a_reply_box_but_no_notes_history_or_actions", async () => {
    vi.mocked(fetch)
      .mockResolvedValueOnce(jsonResponse(baseTicket))
      .mockResolvedValueOnce(jsonResponse(slaSnapshot));

    renderPage();

    await waitFor(() => expect(screen.getByText("Invoice issue")).toBeInTheDocument());

    expect(screen.getByLabelText("Reply box")).toBeInTheDocument();
    expect(screen.queryByText("Internal notes")).not.toBeInTheDocument();
    expect(screen.queryByText("History")).not.toBeInTheDocument();
    expect(screen.queryByText("Actions")).not.toBeInTheDocument();
  });

  it("AC-08 customer reply posts and reloads the ticket", async () => {
    vi.mocked(fetch)
      .mockResolvedValueOnce(jsonResponse(baseTicket))
      .mockResolvedValueOnce(jsonResponse(slaSnapshot))
      .mockResolvedValueOnce(
        jsonResponse({ id: 1, ticket_id: "HD-000001", author_role: "customer", body: "ack", created_at: "x", status: "OPEN" })
      )
      .mockResolvedValueOnce(jsonResponse({ ...baseTicket, status: "OPEN" }))
      .mockResolvedValueOnce(jsonResponse(slaSnapshot));

    renderPage();

    await waitFor(() => expect(screen.getByLabelText("Reply box")).toBeInTheDocument());
    fireEvent.change(screen.getByLabelText("Reply"), { target: { value: "ack" } });
    fireEvent.click(screen.getByText("Send reply"));

    await waitFor(() => expect(screen.getByTestId("ticket-status")).toHaveTextContent("OPEN"));
  });

  it("E6S1_closed_ticket_hides_the_reply_box", async () => {
    vi.mocked(fetch)
      .mockResolvedValueOnce(jsonResponse({ ...baseTicket, status: "CLOSED" }))
      .mockResolvedValueOnce(jsonResponse(slaSnapshot));

    renderPage();

    await waitFor(() => expect(screen.getByTestId("ticket-status")).toHaveTextContent("CLOSED"));
    expect(screen.queryByLabelText("Reply box")).not.toBeInTheDocument();
  });
});
