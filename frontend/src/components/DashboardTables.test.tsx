import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { DashboardTables } from "./DashboardTables";

const dashboard = {
  open_by_queue: [{ queue: { slug: "billing", name: "Billing" }, count: 3 }],
  breached_by_priority: [{ priority: "High" as const, count: 1 }],
  escalations_in_period: 2,
};

describe("DashboardTables", () => {
  it("renders open_by_queue, breached_by_priority and escalations as tables", () => {
    render(<DashboardTables dashboard={dashboard} />);
    expect(screen.getByTestId("open-by-queue-table")).toBeInTheDocument();
    expect(screen.getByText("Billing")).toBeInTheDocument();
    expect(screen.getByTestId("breached-by-priority-table")).toBeInTheDocument();
    expect(screen.getByText("Escalations in period: 2")).toBeInTheDocument();
  });
});
