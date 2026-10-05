import { render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import type { TicketAssignmentEntry, TicketHistoryEntry } from "../api/types";
import { TicketHistory } from "./TicketHistory";

function historyEntry(
  overrides: Partial<TicketHistoryEntry> & Pick<TicketHistoryEntry, "id" | "event">
): TicketHistoryEntry {
  return {
    ticket_id: "HD-000001",
    from_state: null,
    to_state: null,
    actor_id: "system",
    correlation_id: null,
    created_at: "2026-01-01T10:00:00Z",
    ...overrides,
  };
}

function assignmentEntry(
  overrides: Partial<TicketAssignmentEntry> & Pick<TicketAssignmentEntry, "id" | "to_user_id">
): TicketAssignmentEntry {
  return {
    ticket_id: "HD-000001",
    from_user_id: null,
    actor_id: overrides.to_user_id,
    created_at: "2026-01-01T10:00:00Z",
    ...overrides,
  };
}

function eventLabels(): string[] {
  return screen
    .getAllByRole("listitem")
    .map((item) => item.querySelector(".timeline-event")?.textContent ?? "");
}

describe("TicketHistory event labels", () => {
  it("shows only the event name when neither state is present", () => {
    render(
      <TicketHistory
        history={[historyEntry({ id: 1, event: "ESCALATED" })]}
        assignments={[]}
      />
    );
    expect(eventLabels()).toEqual(["ESCALATED"]);
  });

  it("shows only the target state when the source state is missing", () => {
    render(
      <TicketHistory
        history={[historyEntry({ id: 1, event: "ROUTED", to_state: "OPEN" })]}
        assignments={[]}
      />
    );
    expect(eventLabels()).toEqual(["ROUTED: to OPEN"]);
  });

  it("shows from and to when both states are present", () => {
    render(
      <TicketHistory
        history={[
          historyEntry({
            id: 1,
            event: "STATUS_CHANGED",
            from_state: "OPEN",
            to_state: "IN_PROGRESS",
          }),
        ]}
        assignments={[]}
      />
    );
    expect(eventLabels()).toEqual(["STATUS_CHANGED: OPEN to IN_PROGRESS"]);
  });

  it("shows the source state when only the source is present", () => {
    render(
      <TicketHistory
        history={[historyEntry({ id: 1, event: "CLOSED_REJECTED", from_state: "CLOSED" })]}
        assignments={[]}
      />
    );
    expect(eventLabels()).toEqual(["CLOSED_REJECTED: from CLOSED"]);
  });

  it("never prints a bare dash for a missing state", () => {
    render(
      <TicketHistory
        history={[
          historyEntry({ id: 1, event: "ESCALATED" }),
          historyEntry({ id: 2, event: "ROUTED", to_state: "OPEN" }),
          historyEntry({ id: 3, event: "STATUS_CHANGED", from_state: "OPEN", to_state: "RESOLVED" }),
        ]}
        assignments={[]}
      />
    );
    expect(screen.queryByText(/—/)).not.toBeInTheDocument();
  });
});

describe("TicketHistory assignments", () => {
  it("merges claims and reassignments with history, oldest first", () => {
    render(
      <TicketHistory
        history={[
          historyEntry({ id: 1, event: "ROUTED", to_state: "OPEN", created_at: "2026-01-01T10:00:00Z" }),
          historyEntry({
            id: 2,
            event: "STATUS_CHANGED",
            from_state: "OPEN",
            to_state: "IN_PROGRESS",
            actor_id: "AG-1",
            created_at: "2026-01-01T10:30:00Z",
          }),
        ]}
        assignments={[
          assignmentEntry({ id: 1, to_user_id: "AG-1", created_at: "2026-01-01T10:15:00Z" }),
          assignmentEntry({
            id: 2,
            from_user_id: "AG-1",
            to_user_id: "AG-2",
            actor_id: "AG-2",
            created_at: "2026-01-01T11:00:00Z",
          }),
        ]}
      />
    );
    expect(eventLabels()).toEqual([
      "ROUTED: to OPEN",
      "ASSIGNED: AG-1 claimed",
      "STATUS_CHANGED: OPEN to IN_PROGRESS",
      "REASSIGNED: AG-1 to AG-2",
    ]);
  });

  it("shows actor and UTC time on a reassignment entry", () => {
    render(
      <TicketHistory
        history={[]}
        assignments={[
          assignmentEntry({
            id: 1,
            from_user_id: "AG-1",
            to_user_id: "AG-2",
            actor_id: "AG-2",
            created_at: "2026-01-01T11:00:00Z",
          }),
        ]}
      />
    );
    const item = screen.getByText("REASSIGNED: AG-1 to AG-2").closest("li");
    expect(item).not.toBeNull();
    expect(within(item as HTMLElement).getByText("AG-2 · 1 Jan 2026, 11:00 UTC")).toBeInTheDocument();
  });

  it("shows only the target when the actor is not the assignee", () => {
    render(
      <TicketHistory
        history={[]}
        assignments={[
          assignmentEntry({
            id: 1,
            from_user_id: null,
            to_user_id: "AG-2",
            actor_id: "AG-1",
          }),
        ]}
      />
    );
    expect(eventLabels()).toEqual(["ASSIGNED: to AG-2"]);
    expect(screen.getByText("AG-1 · 1 Jan 2026, 10:00 UTC")).toBeInTheDocument();
  });

  it("renders assignments alone without the empty-state message", () => {
    render(
      <TicketHistory
        history={[]}
        assignments={[assignmentEntry({ id: 1, to_user_id: "AG-1" })]}
      />
    );
    expect(eventLabels()).toEqual(["ASSIGNED: AG-1 claimed"]);
    expect(screen.queryByText("No history yet.")).not.toBeInTheDocument();
  });

  it("shows the empty message when there is no history and no assignments", () => {
    render(<TicketHistory history={[]} assignments={[]} />);
    expect(screen.getByText("No history yet.")).toBeInTheDocument();
  });
});
