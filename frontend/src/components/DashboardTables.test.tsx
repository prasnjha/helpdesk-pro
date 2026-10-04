import { render, screen, within } from "@testing-library/react";
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

    const escalationsTable = screen.getByTestId("escalations-in-period-table");
    expect(escalationsTable).toBeInTheDocument();
    expect(escalationsTable.tagName).toBe("TABLE");
    expect(screen.getByRole("columnheader", { name: "Escalations in period" })).toBeInTheDocument();
    const row = within(escalationsTable).getAllByRole("row")[1];
    expect(within(row).getByRole("cell", { name: "2" })).toBeInTheDocument();
  });
});
