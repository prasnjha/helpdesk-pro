import { render, screen, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { QueueFilters } from "./QueueFilters";

const queues = [
  { slug: "billing", name: "Billing" },
  { slug: "technical", name: "Technical" },
];

describe("QueueFilters", () => {
  it("lists the given queues and priorities", () => {
    render(
      <QueueFilters
        queue="billing"
        queues={queues}
        onQueueChange={vi.fn()}
        priority=""
        priorities={["Critical", "High"]}
        onPriorityChange={vi.fn()}
      />
    );
    expect(screen.getByLabelText("Queue")).toHaveValue("billing");
    expect(screen.getByRole("option", { name: "Technical" })).toBeInTheDocument();
    expect(screen.getByRole("option", { name: "Critical" })).toBeInTheDocument();
  });

  it("calls onQueueChange and onPriorityChange", () => {
    const onQueueChange = vi.fn();
    const onPriorityChange = vi.fn();
    render(
      <QueueFilters
        queue="billing"
        queues={queues}
        onQueueChange={onQueueChange}
        priority=""
        priorities={["Critical", "High"]}
        onPriorityChange={onPriorityChange}
      />
    );
    fireEvent.change(screen.getByLabelText("Queue"), { target: { value: "technical" } });
    expect(onQueueChange).toHaveBeenCalledWith("technical");

    fireEvent.change(screen.getByLabelText("Priority"), { target: { value: "Critical" } });
    expect(onPriorityChange).toHaveBeenCalledWith("Critical");
  });
});
