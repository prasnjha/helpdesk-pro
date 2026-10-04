import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { clearSession, setSession } from "../state/session";
import { KbArticlePage } from "./KbArticlePage";

function jsonResponse(body: unknown): Response {
  return new Response(JSON.stringify(body), { status: 200 });
}

const article = {
  id: 5,
  title: "Reset password",
  body: "Steps...",
  tags: ["password"],
  source_ticket_id: "HD-000001",
  created_by: "AG-1",
  updated_at: "x",
};

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

  it("E5S2_renders_the_article_title_body_and_tags", async () => {
    setSession("tok", "customer", "customer1");
    vi.mocked(fetch).mockResolvedValueOnce(jsonResponse(article));

    renderAt("/kb/5");

    await waitFor(() => expect(screen.getByText("Reset password")).toBeInTheDocument());
    expect(screen.getByText("Steps...")).toBeInTheDocument();
    expect(screen.getByTestId("article-tags")).toHaveTextContent("password");
  });

  it("E5S2_customer_viewing_an_article_sees_no_editor_controls", async () => {
    setSession("tok", "customer", "customer1");
    vi.mocked(fetch).mockResolvedValueOnce(jsonResponse(article));

    renderAt("/kb/5");

    await waitFor(() => expect(screen.getByText("Reset password")).toBeInTheDocument());
    expect(screen.queryByText("Edit")).not.toBeInTheDocument();
    expect(screen.queryByText("Delete")).not.toBeInTheDocument();
  });

  it("E5S2_staff_sees_edit_and_delete_linking_to_the_kb_editor", async () => {
    setSession("tok", "agent", "agent1");
    vi.mocked(fetch).mockResolvedValueOnce(jsonResponse(article));

    renderAt("/kb/5");

    await waitFor(() => expect(screen.getByText("Reset password")).toBeInTheDocument());
    expect(screen.getByRole("link", { name: "Edit" })).toHaveAttribute(
      "href",
      "/agent/kb/5/edit"
    );
  });

  it("E5S2_staff_delete_calls_the_delete_endpoint", async () => {
    setSession("tok", "agent", "agent1");
    vi.mocked(fetch)
      .mockResolvedValueOnce(jsonResponse(article))
      .mockResolvedValueOnce(new Response(null, { status: 204 }));

    renderAt("/kb/5");

    await waitFor(() => expect(screen.getByText("Reset password")).toBeInTheDocument());
    fireEvent.click(screen.getByText("Delete"));

    await waitFor(() => {
      const deleteCall = vi.mocked(fetch).mock.calls.find(([, init]) => (init as RequestInit | undefined)?.method === "DELETE");
      expect(deleteCall).toBeDefined();
    });
  });
});
