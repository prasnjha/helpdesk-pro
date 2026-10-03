import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { TicketForm } from "./TicketForm";

describe("TicketForm", () => {
  it("E2S4_sends_no_request_and_shows_message_for_empty_title", () => {
    const onSubmit = vi.fn();
    render(<TicketForm onSubmit={onSubmit} />);

    fireEvent.click(screen.getByText("Submit"));

    expect(onSubmit).not.toHaveBeenCalled();
    expect(screen.getByRole("alert")).toHaveTextContent("Title is required.");
  });

  it("E2S4_submits_payload_for_a_valid_form", () => {
    const onSubmit = vi.fn();
    render(<TicketForm onSubmit={onSubmit} />);

    fireEvent.change(screen.getByLabelText("Title"), { target: { value: "Invoice issue" } });
    fireEvent.change(screen.getByLabelText("Description"), {
      target: { value: "Billed twice" },
    });
    fireEvent.click(screen.getByText("Submit"));

    expect(onSubmit).toHaveBeenCalledWith({
      title: "Invoice issue",
      description: "Billed twice",
      category: "Billing",
      priority: "Medium",
    });
  });
});
