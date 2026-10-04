import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { SlaBadge } from "./SlaBadge";

describe("SlaBadge", () => {
  it("renders the ON_TRACK state", () => {
    render(<SlaBadge state="ON_TRACK" testId="badge" />);
    expect(screen.getByTestId("badge")).toHaveTextContent("ON_TRACK");
  });

  it("renders the AT_RISK state", () => {
    render(<SlaBadge state="AT_RISK" testId="badge" />);
    expect(screen.getByTestId("badge")).toHaveTextContent("AT_RISK");
  });

  it("renders the BREACHED state", () => {
    render(<SlaBadge state="BREACHED" testId="badge" />);
    expect(screen.getByTestId("badge")).toHaveTextContent("BREACHED");
  });
});
