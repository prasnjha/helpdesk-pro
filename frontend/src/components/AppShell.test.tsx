import { fireEvent, render, screen, within } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { afterEach, describe, expect, it } from "vitest";

import { clearSession, getToken, setSession } from "../state/session";
import { AppShell } from "./AppShell";

function renderShell(path: string): void {
  render(
    <MemoryRouter initialEntries={[path]}>
      <Routes>
        <Route path="/login" element={<div>Login page</div>} />
        <Route element={<AppShell />}>
          <Route path="*" element={<main>Page body</main>} />
        </Route>
      </Routes>
    </MemoryRouter>
  );
}

function navLinkNames(): string[] {
  const nav = screen.getByRole("navigation", { name: "Primary" });
  return within(nav)
    .getAllByRole("link")
    .map((link) => link.textContent ?? "");
}

describe("AppShell", () => {
  afterEach(() => {
    clearSession();
  });

  it("shows the brand, the signed-in username and role, and the page body", () => {
    setSession("tok", "customer", "customer1");
    renderShell("/tickets");

    expect(screen.getByRole("img", { name: "HelpDesk Pro" })).toBeInTheDocument();
    expect(screen.getByText("customer1")).toBeInTheDocument();
    expect(screen.getByText("Customer")).toBeInTheDocument();
    expect(screen.getByText("Page body")).toBeInTheDocument();
  });

  it("gives a customer My tickets, New ticket and Knowledge Base links", () => {
    setSession("tok", "customer", "customer1");
    renderShell("/tickets");
    expect(navLinkNames()).toEqual(["My tickets", "New ticket", "Knowledge Base"]);
  });

  it("gives an agent Agent Queue and Knowledge Base links", () => {
    setSession("tok", "agent", "agent1");
    renderShell("/agent/queues/billing");
    expect(navLinkNames()).toEqual(["Agent Queue", "Knowledge Base"]);
  });

  it("gives an admin Dashboard, SLA policies and Knowledge Base links", () => {
    setSession("tok", "admin", "admin1");
    renderShell("/admin/sla-policies");
    expect(navLinkNames()).toEqual(["Dashboard", "SLA policies", "Knowledge Base"]);
  });

  it("marks the current route's link as the active page", () => {
    setSession("tok", "customer", "customer1");
    renderShell("/tickets/new");
    const nav = screen.getByRole("navigation", { name: "Primary" });
    expect(within(nav).getByRole("link", { name: "New ticket" })).toHaveAttribute("aria-current", "page");
    expect(within(nav).getByRole("link", { name: "My tickets" })).not.toHaveAttribute("aria-current");
  });

  it("keeps My tickets active on a customer ticket detail route", () => {
    setSession("tok", "customer", "customer1");
    renderShell("/tickets/HD-000001");
    const nav = screen.getByRole("navigation", { name: "Primary" });
    expect(within(nav).getByRole("link", { name: "My tickets" })).toHaveAttribute("aria-current", "page");
  });

  it("toggles the navigation drawer from the menu button", () => {
    setSession("tok", "agent", "agent1");
    renderShell("/agent/queues/billing");
    const toggle = screen.getByRole("button", { name: "Open navigation menu" });
    expect(toggle).toHaveAttribute("aria-expanded", "false");

    fireEvent.click(toggle);
    expect(screen.getByRole("button", { name: "Close navigation menu" })).toHaveAttribute(
      "aria-expanded",
      "true"
    );
  });

  it("logs out by clearing the session and returning to the login page", () => {
    setSession("tok", "agent", "agent1");
    renderShell("/agent/queues/billing");

    fireEvent.click(screen.getByRole("button", { name: "Log out" }));

    expect(getToken()).toBeNull();
    expect(screen.getByText("Login page")).toBeInTheDocument();
  });
});
