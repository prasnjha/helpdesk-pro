import { render, screen, waitFor, fireEvent, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { AdminConsolePage } from "./AdminConsolePage";

function jsonResponse(body: unknown): Response {
  return new Response(JSON.stringify(body), { status: 200 });
}

const v1 = {
  id: 2,
  priority: "High",
  version: 1,
  response_minutes: 60,
  resolution_minutes: 480,
  created_by: "system",
  published_at: "2026-01-01T00:00:00Z",
};

const dashboard = {
  open_by_queue: [{ queue: { slug: "billing", name: "Billing" }, count: 3 }],
  breached_by_priority: [{ priority: "High", count: 1 }],
  escalations_in_period: 2,
};

describe("AdminConsolePage", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("E6S2_saving_a_new_version_puts_it_first_in_history", async () => {
    const v2 = { ...v1, id: 3, version: 2, response_minutes: 45, resolution_minutes: 360 };
    vi.mocked(fetch)
      .mockResolvedValueOnce(jsonResponse([v1])) // initial load
      .mockResolvedValueOnce(jsonResponse(dashboard))
      .mockResolvedValueOnce(jsonResponse(v2)) // POST new version
      .mockResolvedValueOnce(jsonResponse([v2, v1])); // reload, newest first

    render(<AdminConsolePage />);

    await waitFor(() => expect(screen.getAllByTestId("policy-row-High")).toHaveLength(1));

    fireEvent.change(screen.getByLabelText("Response minutes"), { target: { value: "45" } });
    fireEvent.change(screen.getByLabelText("Resolution minutes"), { target: { value: "360" } });
    fireEvent.click(screen.getByText("Save new version"));

    await waitFor(() => expect(screen.getAllByTestId("policy-row-High")).toHaveLength(2));
    const rows = screen.getAllByTestId("policy-row-High");
    expect(within(rows[0]).getByText("2")).toBeInTheDocument();
  });

  it("E6S2_dashboard_renders_open_by_queue_breached_by_priority_and_escalations_as_tables", async () => {
    vi.mocked(fetch)
      .mockResolvedValueOnce(jsonResponse([v1]))
      .mockResolvedValueOnce(jsonResponse(dashboard));

    render(<AdminConsolePage />);

    await waitFor(() => expect(screen.getByTestId("open-by-queue-table")).toBeInTheDocument());
    expect(screen.getByTestId("breached-by-priority-table")).toBeInTheDocument();
    expect(screen.getByText("Escalations in period: 2")).toBeInTheDocument();
  });
});
