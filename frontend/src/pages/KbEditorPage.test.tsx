import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { clearSession, setSession } from "../state/session";
import { KbEditorPage } from "./KbEditorPage";

function jsonResponse(body: unknown): Response {
  return new Response(JSON.stringify(body), { status: 200 });
}

function renderAt(path: string): void {
  render(
    <MemoryRouter initialEntries={[path]}>
      <Routes>
        <Route path="/agent/kb/new" element={<KbEditorPage />} />
        <Route path="/agent/kb/:id/edit" element={<KbEditorPage />} />
      </Routes>
    </MemoryRouter>
  );
}

describe("KbEditorPage", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
    setSession("tok", "agent", "agent1");
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    clearSession();
  });

  it("E5S2_creates_an_article_with_the_source_ticket_id_from_the_query_param", async () => {
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

    renderAt("/agent/kb/new?source_ticket_id=HD-000001");

    expect(screen.getByLabelText(/source ticket/i)).toHaveValue("HD-000001");

    fireEvent.change(screen.getByLabelText("Title"), { target: { value: "Reset password" } });
    fireEvent.change(screen.getByLabelText("Body"), { target: { value: "Steps..." } });
    fireEvent.change(screen.getByLabelText("Tags (comma separated)"), {
      target: { value: "password, login" },
    });
    fireEvent.click(screen.getByText("Save"));

    await waitFor(() => {
      const [, init] = vi.mocked(fetch).mock.calls[0];
      expect(JSON.parse((init as RequestInit).body as string)).toMatchObject({
        source_ticket_id: "HD-000001",
        title: "Reset password",
      });
    });
  });

  it("E5S2_loads_and_saves_an_existing_article_for_edit", async () => {
    const existing = {
      id: 5,
      title: "Reset password",
      body: "Steps...",
      tags: ["password"],
      source_ticket_id: "HD-000001",
      created_by: "AG-1",
      updated_at: "x",
    };
    vi.mocked(fetch)
      .mockResolvedValueOnce(jsonResponse(existing))
      .mockResolvedValueOnce(jsonResponse({ ...existing, title: "Reset your password" }));

    renderAt("/agent/kb/5/edit");

    await waitFor(() => expect(screen.getByLabelText("Title")).toHaveValue("Reset password"));

    fireEvent.change(screen.getByLabelText("Title"), { target: { value: "Reset your password" } });
    fireEvent.click(screen.getByText("Save"));

    await waitFor(() => {
      const putCall = vi.mocked(fetch).mock.calls.find(([, init]) => (init as RequestInit | undefined)?.method === "PUT");
      expect(putCall).toBeDefined();
    });
  });
});
