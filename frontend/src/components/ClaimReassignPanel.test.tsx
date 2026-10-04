import { render, screen, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { ClaimReassignPanel } from "./ClaimReassignPanel";

describe("ClaimReassignPanel", () => {
  it("calls onClaim when Claim is clicked", () => {
    const onClaim = vi.fn();
    render(
      <ClaimReassignPanel
        onClaim={onClaim}
        reassignTo=""
        onReassignToChange={vi.fn()}
        onReassign={vi.fn()}
      />
    );
    fireEvent.click(screen.getByRole("button", { name: "Claim" }));
    expect(onClaim).toHaveBeenCalled();
  });

  it("shows the reassign input value and submits the reassign form", () => {
    const onReassign = vi.fn((e: React.FormEvent) => e.preventDefault());
    const onReassignToChange = vi.fn();
    render(
      <ClaimReassignPanel
        onClaim={vi.fn()}
        reassignTo="AG-2"
        onReassignToChange={onReassignToChange}
        onReassign={onReassign}
      />
    );

    const input = screen.getByLabelText("Reassign to (user id)");
    expect(input).toHaveValue("AG-2");

    fireEvent.change(input, { target: { value: "AG-3" } });
    expect(onReassignToChange).toHaveBeenCalledWith("AG-3");

    fireEvent.click(screen.getByRole("button", { name: "Reassign" }));
    expect(onReassign).toHaveBeenCalled();
  });
});
