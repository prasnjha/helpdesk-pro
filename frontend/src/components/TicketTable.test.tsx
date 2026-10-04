import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";

import { TicketTable } from "./TicketTable";

const tickets = [
  {
    id: "HD-000001",
    title: "Critical outage",
    priority: "Critical" as const,
    status: "OPEN" as const,
    queue: { slug: "billing", name: "Billing" },
    assignee_id: null,
    escalated: false,
    response_state: "BREACHED" as const,
    resolution_state: "ON_TRACK" as const,
  },
  {
    id: "HD-000002",
    title: "Minor question",
    priority: "Low" as const,
    status: "OPEN" as const,
    queue: { slug: "billing", name: "Billing" },
    assignee_id: null,
    escalated: false,
    response_state: "ON_TRACK" as const,
    resolution_state: "ON_TRACK" as const,
  },
];

describe("TicketTable", () => {
  it("renders a row per ticket with the worst SLA state", () => {
    render(
      <MemoryRouter>
        <TicketTable tickets={tickets} />
      </MemoryRouter>
    );
    expect(screen.getAllByTestId("queue-row")).toHaveLength(2);
    const states = screen.getAllByTestId("queue-row-sla-state").map((el) => el.textContent);
    expect(states).toEqual(["BREACHED", "ON_TRACK"]);
  });

  it("links each row to the agent ticket page", () => {
    render(
      <MemoryRouter>
        <TicketTable tickets={tickets} />
      </MemoryRouter>
    );
    expect(screen.getByRole("link", { name: "HD-000001" })).toHaveAttribute(
      "href",
      "/agent/tickets/HD-000001"
    );
  });
});
