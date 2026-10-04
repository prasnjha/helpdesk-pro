import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { ThreadPanel } from "./ThreadPanel";

const replies = [
  { id: 1, ticket_id: "HD-1", author_id: "C-1", author_role: "customer", body: "Hello", created_at: "x" },
];

const notes = [{ id: 1, ticket_id: "HD-1", author_id: "AG-1", body: "Internal note", created_at: "x" }];

describe("ThreadPanel", () => {
  it("renders replies with the author role", () => {
    render(<ThreadPanel replies={replies} notes={[]} showNotes={false} />);
    expect(screen.getByText("customer:")).toBeInTheDocument();
    expect(screen.getByText("Hello")).toBeInTheDocument();
    expect(screen.queryByText("Internal notes")).not.toBeInTheDocument();
  });

  it("renders notes only when showNotes is true", () => {
    render(<ThreadPanel replies={replies} notes={notes} showNotes />);
    expect(screen.getByText("Internal notes")).toBeInTheDocument();
    expect(screen.getByText("Internal note")).toBeInTheDocument();
  });

  it("renders the passed reply box and note form slots", () => {
    render(
      <ThreadPanel
        replies={replies}
        notes={notes}
        showNotes
        replyBox={<div data-testid="reply-slot" />}
        noteForm={<div data-testid="note-slot" />}
      />
    );
    expect(screen.getByTestId("reply-slot")).toBeInTheDocument();
    expect(screen.getByTestId("note-slot")).toBeInTheDocument();
  });
});
