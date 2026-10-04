import { render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { PolicyHistoryTable } from "./PolicyHistoryTable";

const rows = [
  {
    id: 3,
    priority: "High" as const,
    version: 2,
    response_minutes: 45,
    resolution_minutes: 360,
    created_by: "admin1",
    published_at: "2026-02-01T00:00:00Z",
  },
  {
    id: 2,
    priority: "High" as const,
    version: 1,
    response_minutes: 60,
    resolution_minutes: 480,
    created_by: "system",
    published_at: "2026-01-01T00:00:00Z",
  },
];

describe("PolicyHistoryTable", () => {
  it("renders versions newest first as given, under the priority heading", () => {
    render(<PolicyHistoryTable priority="High" rows={rows} />);
    expect(screen.getByText("High")).toBeInTheDocument();
    const rowEls = screen.getAllByTestId("policy-row-High");
    expect(rowEls).toHaveLength(2);
    expect(within(rowEls[0]).getByText("2")).toBeInTheDocument();
    expect(within(rowEls[1]).getByText("1")).toBeInTheDocument();
  });
});
