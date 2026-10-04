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
});
