import { render, screen, waitFor, fireEvent, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { AdminPoliciesPage } from "./AdminPoliciesPage";

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

describe("AdminPoliciesPage", () => {
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
      .mockResolvedValueOnce(jsonResponse(v2)) // POST new version
      .mockResolvedValueOnce(jsonResponse([v2, v1])); // reload, newest first

    render(<AdminPoliciesPage />);

    await waitFor(() => expect(screen.getAllByTestId("policy-row-High")).toHaveLength(1));

    fireEvent.change(screen.getByLabelText("Response minutes"), { target: { value: "45" } });
    fireEvent.change(screen.getByLabelText("Resolution minutes"), { target: { value: "360" } });
    fireEvent.click(screen.getByText("Save new version"));

    await waitFor(() => expect(screen.getAllByTestId("policy-row-High")).toHaveLength(2));
    const rows = screen.getAllByTestId("policy-row-High");
    expect(within(rows[0]).getByText("2")).toBeInTheDocument();
  });
});
