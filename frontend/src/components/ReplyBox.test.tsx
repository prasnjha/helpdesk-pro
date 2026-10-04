import { render, screen, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { ReplyBox } from "./ReplyBox";

describe("ReplyBox", () => {
  it("shows the current value and calls onChange when typed into", () => {
    const onChange = vi.fn();
    render(<ReplyBox value="draft" onChange={onChange} onSubmit={vi.fn()} />);

    const textarea = screen.getByLabelText("Reply");
    expect(textarea).toHaveValue("draft");

    fireEvent.change(textarea, { target: { value: "draft text" } });
    expect(onChange).toHaveBeenCalledWith("draft text");
  });

  it("calls onSubmit when the form is submitted", () => {
    const onSubmit = vi.fn((e: React.FormEvent) => e.preventDefault());
    render(<ReplyBox value="" onChange={vi.fn()} onSubmit={onSubmit} />);

    fireEvent.click(screen.getByRole("button", { name: "Send reply" }));
    expect(onSubmit).toHaveBeenCalled();
  });

  it("has the Reply box accessible name", () => {
    render(<ReplyBox value="" onChange={vi.fn()} onSubmit={vi.fn()} />);
    expect(screen.getByRole("textbox", { name: "Reply" })).toBeInTheDocument();
  });
});
