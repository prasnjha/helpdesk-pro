import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { ErrorBanner } from "./ErrorBanner";

describe("ErrorBanner", () => {
  it("E1S1_renders_nothing_when_message_is_null", () => {
    const { container } = render(<ErrorBanner message={null} />);
    expect(container).toBeEmptyDOMElement();
  });

  it("E1S1_renders_the_error_message", () => {
    render(<ErrorBanner message="Incorrect username or password" />);
    expect(screen.getByRole("alert")).toHaveTextContent("Incorrect username or password");
  });
});
