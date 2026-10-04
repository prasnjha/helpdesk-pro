import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { Button } from "./Button";
import { Card } from "./Card";
import { EscalatedTag } from "./EscalatedTag";
import { PriorityBadge } from "./PriorityBadge";
import { SlaBadge } from "./SlaBadge";
import { StatusChip } from "./StatusChip";

describe("StatusChip", () => {
  it.each([
    ["OPEN", "chip-open"],
    ["IN_PROGRESS", "chip-warning"],
    ["PENDING_CUSTOMER", "chip-pending"],
    ["RESOLVED", "chip-resolved"],
    ["CLOSED", "chip-closed"],
  ] as const)("renders %s verbatim with the %s palette", (status, className) => {
    render(<StatusChip status={status} testId="chip" />);
    const chip = screen.getByTestId("chip");
    expect(chip).toHaveTextContent(status);
    expect(chip.textContent).toBe(status);
    expect(chip).toHaveClass("chip", className);
  });

  it("falls back to the neutral palette for an unknown status string", () => {
    render(<StatusChip status="SOMETHING_ELSE" testId="chip" />);
    expect(screen.getByTestId("chip")).toHaveClass("chip", "chip-closed");
  });
});

describe("PriorityBadge", () => {
  it.each(["Critical", "High", "Medium", "Low"] as const)("renders %s with its own class", (priority) => {
    render(<PriorityBadge priority={priority} />);
    const badge = screen.getByText(priority);
    expect(badge).toHaveClass("priority", `priority-${priority.toLowerCase()}`);
  });
});

describe("SlaBadge palette", () => {
  it.each([
    ["ON_TRACK", "chip-resolved"],
    ["AT_RISK", "chip-warning"],
    ["BREACHED", "chip-critical"],
  ] as const)("uses the %s colour mapping", (state, className) => {
    render(<SlaBadge state={state} testId="badge" />);
    const badge = screen.getByTestId("badge");
    expect(badge.textContent).toBe(state);
    expect(badge).toHaveClass("chip", className);
  });
});

describe("EscalatedTag", () => {
  it("renders the escalated flag with the critical tag style", () => {
    render(<EscalatedTag testId="tag" />);
    expect(screen.getByTestId("tag")).toHaveTextContent("Escalated");
    expect(screen.getByTestId("tag")).toHaveClass("tag-escalated");
  });
});

describe("Button", () => {
  it("defaults to the primary variant and forwards clicks", () => {
    const onClick = vi.fn();
    render(<Button onClick={onClick}>Save</Button>);
    const button = screen.getByRole("button", { name: "Save" });
    expect(button).toHaveAttribute("type", "button");
    expect(button).not.toHaveClass("btn-secondary");
    fireEvent.click(button);
    expect(onClick).toHaveBeenCalled();
  });

  it("applies the secondary and danger variants", () => {
    render(
      <>
        <Button variant="secondary">Cancel</Button>
        <Button variant="danger" type="submit">
          Delete
        </Button>
      </>
    );
    expect(screen.getByRole("button", { name: "Cancel" })).toHaveClass("btn-secondary");
    const danger = screen.getByRole("button", { name: "Delete" });
    expect(danger).toHaveClass("btn-danger");
    expect(danger).toHaveAttribute("type", "submit");
  });
});

describe("Card", () => {
  it("renders an optional titled header with actions and the body", () => {
    render(
      <Card title="SLA status" actions={<span>Live</span>}>
        <p>Body</p>
      </Card>
    );
    expect(screen.getByRole("heading", { name: "SLA status" })).toBeInTheDocument();
    expect(screen.getByText("Live")).toBeInTheDocument();
    expect(screen.getByText("Body")).toBeInTheDocument();
  });

  it("renders as a labelled section when given an aria-label", () => {
    render(
      <Card ariaLabel="History">
        <p>Body</p>
      </Card>
    );
    expect(screen.getByRole("region", { name: "History" })).toBeInTheDocument();
  });
});
