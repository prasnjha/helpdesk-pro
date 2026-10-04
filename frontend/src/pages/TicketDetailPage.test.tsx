import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { clearSession, setSession } from "../state/session";
import { TicketDetailPage } from "./TicketDetailPage";

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), { status });
}

const baseTicket = {
  id: "HD-000001",
  title: "Invoice issue",
  description: "Billed twice",
  category: "Billing",
  priority: "High",
  status: "OPEN",
  queue: { slug: "billing", name: "Billing" },
  customer_id: "C-1",
  assignee_id: null,
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
        <Route path="/tickets/:id" element={<TicketDetailPage />} />
      </Routes>
    </MemoryRouter>
  );
}

describe("TicketDetailPage", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    clearSession();
  });

  it("E6S3_customer_sees_a_reply_box_but_no_notes_history_or_actions", async () => {
    setSession("tok", "customer", "customer1");
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

  it("E6S1_agent_claim_updates_assignee_without_a_page_reload", async () => {
    setSession("tok", "agent", "agent1");
    vi.mocked(fetch)
      .mockResolvedValueOnce(jsonResponse(baseTicket))
      .mockResolvedValueOnce(jsonResponse(slaSnapshot))
      .mockResolvedValueOnce(jsonResponse({ id: "HD-000001", status: "IN_PROGRESS", assignee_id: "AG-1" }))
      .mockResolvedValueOnce(jsonResponse({ ...baseTicket, status: "IN_PROGRESS", assignee_id: "AG-1", version: 2 }))
      .mockResolvedValueOnce(jsonResponse(slaSnapshot));

    renderPage();

    await waitFor(() => expect(screen.getByTestId("ticket-assignee")).toHaveTextContent("Unassigned"));

    fireEvent.click(screen.getByText("Claim"));

    await waitFor(() => expect(screen.getByTestId("ticket-assignee")).toHaveTextContent("AG-1"));
    expect(screen.getByTestId("ticket-status")).toHaveTextContent("IN_PROGRESS");

    const claimCall = vi.mocked(fetch).mock.calls.find(([url]) => String(url).includes("/claim"));
    expect(claimCall).toBeDefined();
  });

  it("E6S1_status_control_only_offers_the_valid_next_states_for_in_progress", async () => {
    setSession("tok", "agent", "agent1");
    vi.mocked(fetch)
      .mockResolvedValueOnce(jsonResponse({ ...baseTicket, status: "IN_PROGRESS" }))
      .mockResolvedValueOnce(jsonResponse(slaSnapshot));

    renderPage();

    await waitFor(() => expect(screen.getByTestId("ticket-status")).toHaveTextContent("IN_PROGRESS"));

    const select = screen.getByLabelText("Change status") as HTMLSelectElement;
    const offered = Array.from(select.options).map((o) => o.value);
    expect(offered).toEqual(["PENDING_CUSTOMER", "RESOLVED"]);
  });

  it("E6S1_invalid_status_change_surfaces_the_409_message_through_error_banner", async () => {
    setSession("tok", "agent", "agent1");
    vi.mocked(fetch)
      .mockResolvedValueOnce(jsonResponse({ ...baseTicket, status: "OPEN" }))
      .mockResolvedValueOnce(jsonResponse(slaSnapshot))
      .mockResolvedValueOnce(
        jsonResponse({ error: { code: "INVALID_TICKET_STATE", message: "That transition is not allowed." } }, 409)
      );

    renderPage();

    await waitFor(() => expect(screen.getByTestId("ticket-status")).toHaveTextContent("OPEN"));
    fireEvent.click(screen.getByText("Update status"));

    await waitFor(() =>
      expect(screen.getByText("That transition is not allowed.")).toBeInTheDocument()
    );
  });

  it("E6S1_closed_ticket_is_read_only_for_agents", async () => {
    setSession("tok", "agent", "agent1");
    vi.mocked(fetch)
      .mockResolvedValueOnce(jsonResponse({ ...baseTicket, status: "CLOSED" }))
      .mockResolvedValueOnce(jsonResponse(slaSnapshot));

    renderPage();

    await waitFor(() => expect(screen.getByTestId("ticket-status")).toHaveTextContent("CLOSED"));

    expect(screen.getByText("Closed tickets cannot be changed.")).toBeInTheDocument();
    expect(screen.queryByText("Claim")).not.toBeInTheDocument();
    expect(screen.queryByText("Update status")).not.toBeInTheDocument();
    expect(screen.queryByLabelText("Reply box")).not.toBeInTheDocument();
  });
});
