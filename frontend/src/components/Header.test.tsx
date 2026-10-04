import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";

import { Header } from "./Header";

describe("Header", () => {
  it("shows the HelpDesk Pro logo and name", () => {
    render(
      <MemoryRouter>
        <Header />
      </MemoryRouter>
    );

    expect(screen.getByRole("img", { name: "HelpDesk Pro" })).toBeInTheDocument();
    expect(screen.getByText("HelpDesk Pro")).toBeInTheDocument();
  });
});
