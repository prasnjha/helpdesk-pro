import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { clearSession, setSession } from "../state/session";
import { KbArticlePage } from "./KbArticlePage";

function jsonResponse(body: unknown): Response {
  return new Response(JSON.stringify(body), { status: 200 });
}

function renderAt(path: string): void {
  render(
    <MemoryRouter initialEntries={[path]}>
      <Routes>
        <Route path="/kb/:id" element={<KbArticlePage />} />
      </Routes>
    </MemoryRouter>
  );
}

describe("KbArticlePage", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    clearSession();
  });

  it("E5S2_agent_saves_an_article_with_tags_and_the_saved_article_shows_them", async () => {
    setSession("tok", "agent", "agent1");
    const created = {
      id: 5,
      title: "Reset password",
      body: "Steps...",
      tags: ["password", "login"],
      source_ticket_id: "HD-000001",
      created_by: "AG-1",
      updated_at: "x",
    };
    vi.mocked(fetch).mockResolvedValueOnce(jsonResponse(created));

    renderAt("/kb/new?source_ticket_id=HD-000001");

    fireEvent.change(screen.getByLabelText("Title"), { target: { value: "Reset password" } });
    fireEvent.change(screen.getByLabelText("Body"), { target: { value: "Steps..." } });
    fireEvent.change(screen.getByLabelText("Tags (comma separated)"), {
      target: { value: "password, login" },
    });

    vi.mocked(fetch).mockResolvedValueOnce(jsonResponse(created)); // GET after navigate to /kb/5
    fireEvent.click(screen.getByText("Save"));

    await waitFor(() => expect(screen.getByTestId("article-tags")).toHaveTextContent("password, login"));
  });

  it("E5S2_customer_viewing_an_article_sees_no_editor_controls", async () => {
    setSession("tok", "customer", "customer1");
    const article = {
      id: 5,
      title: "Reset password",
      body: "Steps...",
      tags: ["password"],
      source_ticket_id: "HD-000001",
      created_by: "AG-1",
      updated_at: "x",
    };
    vi.mocked(fetch).mockResolvedValueOnce(jsonResponse(article));

    renderAt("/kb/5");

    await waitFor(() => expect(screen.getByText("Reset password")).toBeInTheDocument());
    expect(screen.queryByText("Edit")).not.toBeInTheDocument();
    expect(screen.queryByText("Delete")).not.toBeInTheDocument();
  });
});
