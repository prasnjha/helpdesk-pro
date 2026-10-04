import { render, screen, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { PolicyEditor } from "./PolicyEditor";

describe("PolicyEditor", () => {
  it("shows the current field values and calls the change handlers", () => {
    const onPriorityChange = vi.fn();
    const onResponseMinutesChange = vi.fn();
    const onResolutionMinutesChange = vi.fn();
    render(
      <PolicyEditor
        priority="High"
        priorities={["Critical", "High", "Medium", "Low"]}
        onPriorityChange={onPriorityChange}
        responseMinutes="60"
        onResponseMinutesChange={onResponseMinutesChange}
        resolutionMinutes="480"
        onResolutionMinutesChange={onResolutionMinutesChange}
        onSubmit={vi.fn()}
      />
    );

    expect(screen.getByLabelText("Response minutes")).toHaveValue("60");
    expect(screen.getByLabelText("Resolution minutes")).toHaveValue("480");

    fireEvent.change(screen.getByLabelText("Priority"), { target: { value: "Critical" } });
    expect(onPriorityChange).toHaveBeenCalledWith("Critical");

    fireEvent.change(screen.getByLabelText("Response minutes"), { target: { value: "45" } });
    expect(onResponseMinutesChange).toHaveBeenCalledWith("45");

    fireEvent.change(screen.getByLabelText("Resolution minutes"), { target: { value: "360" } });
    expect(onResolutionMinutesChange).toHaveBeenCalledWith("360");
  });

  it("calls onSubmit when saving", () => {
    const onSubmit = vi.fn((e: React.FormEvent) => e.preventDefault());
    render(
      <PolicyEditor
        priority="High"
        priorities={["Critical", "High", "Medium", "Low"]}
        onPriorityChange={vi.fn()}
        responseMinutes="60"
        onResponseMinutesChange={vi.fn()}
        resolutionMinutes="480"
        onResolutionMinutesChange={vi.fn()}
        onSubmit={onSubmit}
      />
    );
    fireEvent.click(screen.getByText("Save new version"));
    expect(onSubmit).toHaveBeenCalled();
  });
});
