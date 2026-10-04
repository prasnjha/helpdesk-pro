import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { clearSession, setSession } from "../state/session";
import { AgentTicketPage } from "./AgentTicketPage";

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
    <MemoryRouter initialEntries={["/agent/tickets/HD-000001"]}>
      <Routes>
        <Route path="/agent/tickets/:id" element={<AgentTicketPage />} />
      </Routes>
    </MemoryRouter>
  );
}

describe("AgentTicketPage", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
    setSession("tok", "agent", "agent1");
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    clearSession();
  });

  it("E6S1_agent_claim_updates_assignee_without_a_page_reload", async () => {
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

  it("E6S1_shows_internal_notes_and_history_for_staff", async () => {
    vi.mocked(fetch)
      .mockResolvedValueOnce(
        jsonResponse({
          ...baseTicket,
          notes: [{ id: 1, ticket_id: "HD-000001", author_id: "agent1", body: "checked billing", created_at: "x" }],
          history: [{ id: 1, ticket_id: "HD-000001", event: "CREATED", from_state: null, to_state: "OPEN", actor_id: "C-1", correlation_id: null, created_at: "x" }],
        })
      )
      .mockResolvedValueOnce(jsonResponse(slaSnapshot));

    renderPage();

    await waitFor(() => expect(screen.getByText("checked billing")).toBeInTheDocument());
    expect(screen.getByText("History")).toBeInTheDocument();
  });

  it("E5S2_publish_to_kb_link_is_visible_once_resolved", async () => {
    vi.mocked(fetch)
      .mockResolvedValueOnce(jsonResponse({ ...baseTicket, status: "RESOLVED" }))
      .mockResolvedValueOnce(jsonResponse(slaSnapshot));

    renderPage();

    await waitFor(() => expect(screen.getByTestId("ticket-status")).toHaveTextContent("RESOLVED"));
    expect(screen.getByRole("link", { name: "Publish to knowledge base" })).toHaveAttribute(
      "href",
      "/agent/kb/new?source_ticket_id=HD-000001"
    );
  });
});
