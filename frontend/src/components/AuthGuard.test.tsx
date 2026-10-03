import { render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { afterEach, describe, expect, it } from "vitest";

import { clearToken, setToken } from "../state/session";
import { AuthGuard } from "./AuthGuard";

describe("AuthGuard", () => {
  afterEach(() => {
    clearToken();
  });

  it("E2S4_redirects_to_login_without_a_token", () => {
    render(
      <MemoryRouter initialEntries={["/tickets"]}>
        <Routes>
          <Route path="/login" element={<div>Login page</div>} />
          <Route
            path="/tickets"
            element={
              <AuthGuard>
                <div>Secret tickets</div>
              </AuthGuard>
            }
          />
        </Routes>
      </MemoryRouter>
    );
    expect(screen.getByText("Login page")).toBeInTheDocument();
  });

  it("E2S4_renders_children_when_a_token_is_present", () => {
    setToken("a-token");
    render(
      <MemoryRouter initialEntries={["/tickets"]}>
        <Routes>
          <Route path="/login" element={<div>Login page</div>} />
          <Route
            path="/tickets"
            element={
              <AuthGuard>
                <div>Secret tickets</div>
              </AuthGuard>
            }
          />
        </Routes>
      </MemoryRouter>
    );
    expect(screen.getByText("Secret tickets")).toBeInTheDocument();
  });
});
