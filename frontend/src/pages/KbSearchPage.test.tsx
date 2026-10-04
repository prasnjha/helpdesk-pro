import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { clearSession, setSession } from "../state/session";
import { KbSearchPage } from "./KbSearchPage";

function jsonResponse(body: unknown): Response {
  return new Response(JSON.stringify(body), { status: 200 });
}

const articles = [{ id: 1, title: "Reset your password", tags: ["password"], updated_at: "x" }];

describe("KbSearchPage", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    clearSession();
  });

  it("E5S2_customer_search_for_password_lists_matching_titles", async () => {
    setSession("tok", "customer", "customer1");
    vi.mocked(fetch)
      .mockResolvedValueOnce(jsonResponse([]))
      .mockResolvedValueOnce(jsonResponse(articles));

    render(
      <MemoryRouter>
        <KbSearchPage />
      </MemoryRouter>
    );

    fireEvent.change(screen.getByLabelText("Search"), { target: { value: "password" } });

    await waitFor(() => expect(screen.getByText("Reset your password")).toBeInTheDocument());
    const [lastUrl] = vi.mocked(fetch).mock.calls[vi.mocked(fetch).mock.calls.length - 1];
    expect(String(lastUrl)).toContain("q=password");
  });

  it("E5S2_customer_sees_no_editor_controls", async () => {
    setSession("tok", "customer", "customer1");
    vi.mocked(fetch).mockResolvedValueOnce(jsonResponse(articles));

    render(
      <MemoryRouter>
        <KbSearchPage />
      </MemoryRouter>
    );

    await waitFor(() => expect(screen.getByText("Reset your password")).toBeInTheDocument());
    expect(screen.queryByText("New article")).not.toBeInTheDocument();
  });

  it("E5S2_agent_sees_a_new_article_link_to_the_kb_editor", async () => {
    setSession("tok", "agent", "agent1");
    vi.mocked(fetch).mockResolvedValueOnce(jsonResponse(articles));

    render(
      <MemoryRouter>
        <KbSearchPage />
      </MemoryRouter>
    );

    await waitFor(() => expect(screen.getByText("New article")).toBeInTheDocument());
    expect(screen.getByRole("link", { name: "New article" })).toHaveAttribute(
      "href",
      "/agent/kb/new"
    );
  });
});
