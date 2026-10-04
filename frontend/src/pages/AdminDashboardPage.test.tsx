import { render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { AdminDashboardPage } from "./AdminDashboardPage";

function jsonResponse(body: unknown): Response {
  return new Response(JSON.stringify(body), { status: 200 });
}

const dashboard = {
  open_by_queue: [{ queue: { slug: "billing", name: "Billing" }, count: 3 }],
  breached_by_priority: [{ priority: "High", count: 1 }],
  escalations_in_period: 2,
};

describe("AdminDashboardPage", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("E6S2_dashboard_renders_open_by_queue_breached_by_priority_and_escalations_as_tables", async () => {
    vi.mocked(fetch).mockResolvedValueOnce(jsonResponse(dashboard));

    render(<AdminDashboardPage />);

    await waitFor(() => expect(screen.getByTestId("open-by-queue-table")).toBeInTheDocument());
    expect(screen.getByTestId("breached-by-priority-table")).toBeInTheDocument();
    expect(screen.getByText("Escalations in period: 2")).toBeInTheDocument();
  });
});
