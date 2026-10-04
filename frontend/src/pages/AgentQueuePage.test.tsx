import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { AgentQueuePage } from "./AgentQueuePage";

function jsonResponse(body: unknown): Response {
  return new Response(JSON.stringify(body), { status: 200 });
}

const tickets = [
  {
    id: "HD-000001",
    title: "Critical outage",
    priority: "Critical",
    status: "OPEN",
    queue: { slug: "billing", name: "Billing" },
    assignee_id: null,
    escalated: false,
    response_state: "BREACHED",
    resolution_state: "ON_TRACK",
  },
  {
    id: "HD-000002",
    title: "Minor question",
    priority: "Low",
    status: "OPEN",
    queue: { slug: "billing", name: "Billing" },
    assignee_id: null,
    escalated: false,
    response_state: "ON_TRACK",
    resolution_state: "ON_TRACK",
  },
];

describe("AgentQueuePage", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("E6S1_lists_tickets_for_the_selected_queue_and_shows_breached_state", async () => {
    vi.mocked(fetch).mockResolvedValueOnce(jsonResponse(tickets));

    render(
      <MemoryRouter>
        <AgentQueuePage />
      </MemoryRouter>
    );

    await waitFor(() => expect(screen.getAllByTestId("queue-row")).toHaveLength(2));
    const states = screen.getAllByTestId("queue-row-sla-state").map((el) => el.textContent);
    expect(states).toEqual(["BREACHED", "ON_TRACK"]);
  });

  it("E6S1_filtering_by_priority_requests_only_that_priority", async () => {
    vi.mocked(fetch)
      .mockResolvedValueOnce(jsonResponse(tickets))
      .mockResolvedValueOnce(jsonResponse([tickets[0]]));

    render(
      <MemoryRouter>
        <AgentQueuePage />
      </MemoryRouter>
    );

    await waitFor(() => expect(screen.getAllByTestId("queue-row")).toHaveLength(2));

    fireEvent.change(screen.getByLabelText("Priority"), { target: { value: "Critical" } });

    await waitFor(() => expect(screen.getAllByTestId("queue-row")).toHaveLength(1));
    const [lastUrl] = vi.mocked(fetch).mock.calls[vi.mocked(fetch).mock.calls.length - 1];
    expect(String(lastUrl)).toContain("priority=Critical");
  });
});
