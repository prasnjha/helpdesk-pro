import { render, screen, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { StatusControl } from "./StatusControl";

describe("StatusControl", () => {
  it("offers only the given next states", () => {
    render(
      <StatusControl
        nextStates={["PENDING_CUSTOMER", "RESOLVED"]}
        selected="PENDING_CUSTOMER"
        onChange={vi.fn()}
        onSubmit={vi.fn()}
      />
    );
    const select = screen.getByLabelText("Change status") as HTMLSelectElement;
    expect(Array.from(select.options).map((o) => o.value)).toEqual([
      "PENDING_CUSTOMER",
      "RESOLVED",
    ]);
  });

  it("renders nothing when there are no next states", () => {
    render(
      <StatusControl nextStates={[]} selected="" onChange={vi.fn()} onSubmit={vi.fn()} />
    );
    expect(screen.queryByLabelText("Change status")).not.toBeInTheDocument();
  });

  it("calls onSubmit when Update status is clicked", () => {
    const onSubmit = vi.fn((e: React.FormEvent) => e.preventDefault());
    render(
      <StatusControl
        nextStates={["RESOLVED"]}
        selected="RESOLVED"
        onChange={vi.fn()}
        onSubmit={onSubmit}
      />
    );
    fireEvent.click(screen.getByRole("button", { name: "Update status" }));
    expect(onSubmit).toHaveBeenCalled();
  });
});
