import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import type { SlaSnapshot, TicketDetail } from "../api/types";
import { SlaPanel } from "./SlaPanel";
import { TicketHeader } from "./TicketHeader";

const ticket: TicketDetail = {
  id: "HD-000001",
  title: "Invoice issue",
  description: "Billed twice",
  category: "Billing",
  priority: "High",
  status: "IN_PROGRESS",
  queue: { slug: "billing-tier-2", name: "Billing Tier 2" },
  customer_id: "C-1",
  assignee_id: null,
  escalated: true,
  version: 1,
  sla_policy_version_id: 1,
  created_at: "2026-01-01T00:00:00Z",
  updated_at: "2026-01-01T00:00:00Z",
  replies: [],
  notes: [],
  history: [],
  assignments: [],
};

describe("TicketHeader", () => {
  it("shows the title, description, status, assignee and escalated flag", () => {
    render(<TicketHeader ticket={ticket} />);

    expect(screen.getByRole("heading", { name: "Invoice issue" })).toBeInTheDocument();
    expect(screen.getByText("Billed twice")).toBeInTheDocument();
    expect(screen.getByTestId("ticket-status")).toHaveTextContent("IN_PROGRESS");
    expect(screen.getByTestId("ticket-assignee")).toHaveTextContent("Unassigned");
    expect(screen.getByTestId("ticket-escalated")).toHaveTextContent("Escalated");
    expect(screen.getByText("Billing Tier 2")).toBeInTheDocument();
    expect(screen.getByText("1 Jan 2026")).toBeInTheDocument();
  });

  it("omits the escalated flag when the ticket is not escalated", () => {
    render(<TicketHeader ticket={{ ...ticket, escalated: false, assignee_id: "AG-1" }} />);
    expect(screen.queryByTestId("ticket-escalated")).not.toBeInTheDocument();
    expect(screen.getByTestId("ticket-assignee")).toHaveTextContent("AG-1");
  });
});

describe("SlaPanel", () => {
  const sla: SlaSnapshot = {
    response: { target_minutes: 60, elapsed_minutes: 75, state: "BREACHED", stopped_at: null },
    resolution: { target_minutes: 480, elapsed_minutes: 120, state: "ON_TRACK", stopped_at: null },
  };

  it("shows each timer's state and integer minutes", () => {
    render(<SlaPanel sla={sla} />);

    expect(screen.getByTestId("sla-response-state")).toHaveTextContent("BREACHED");
    expect(screen.getByTestId("sla-resolution-state")).toHaveTextContent("ON_TRACK");
    expect(screen.getByText("75 of 60 min elapsed")).toBeInTheDocument();
    expect(screen.getByText("120 of 480 min elapsed")).toBeInTheDocument();
  });
});
