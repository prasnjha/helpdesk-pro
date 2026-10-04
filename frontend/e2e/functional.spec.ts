import { expect, test, type Page } from "@playwright/test";

// Functional E2E coverage for Group D: login per role, create a ticket,
// agent claim, a valid and an invalid status change (409 surfaced), a
// customer reply on PENDING_CUSTOMER, and a closed ticket read-only. These
// only need to run once (viewport doesn't change the outcome), so they are
// gated to the desktop-1280 project the same way responsive.spec.ts gates
// its per-breakpoint checks.

async function login(page: Page, username: string, password = "Password123!"): Promise<void> {
  await page.goto("/login");
  await page.getByLabel("Username").fill(username);
  await page.getByLabel("Password").fill(password);
  await page.getByRole("button", { name: "Sign in" }).click();
}

test.beforeEach(({ page }, testInfo) => {
  test.skip(testInfo.project.name !== "desktop-1280", "functional flows run once, not per breakpoint");
  void page;
});

test("E2S4_customer_login_lands_on_my_tickets", async ({ page }) => {
  await login(page, "customer1");
  await expect(page).toHaveURL(/\/tickets$/);
  await expect(page.getByRole("heading", { name: "My tickets" })).toBeVisible();
});

test("E2S4_agent_login_lands_on_agent_workbench", async ({ page }) => {
  await login(page, "agent1");
  await expect(page).toHaveURL(/\/agent\/queues$/);
  await expect(page.getByRole("heading", { name: "Agent workbench" })).toBeVisible();
});

test("E2S4_admin_login_lands_on_admin_console", async ({ page }) => {
  await login(page, "admin1");
  await expect(page).toHaveURL(/\/admin$/);
});

test.describe("ticket lifecycle", () => {
  test.describe.configure({ mode: "serial" });

  let ticketId = "";

  test("E2S4_customer_creates_a_ticket", async ({ page }) => {
    await login(page, "customer1");
    await page.getByRole("link", { name: "New ticket" }).click();
    await page.getByLabel("Title").fill("E2E: VPN keeps disconnecting");
    await page.getByLabel("Description").fill("Happens every few minutes on the Billing VPN.");
    await page.getByLabel("Category").selectOption("Billing");
    await page.getByLabel("Priority").selectOption("High");
    await page.getByRole("button", { name: "Submit" }).click();

    await expect(page.getByRole("heading", { name: "Ticket created" })).toBeVisible();
    const idMatch = await page.getByText(/is OPEN\./).textContent();
    ticketId = idMatch?.split(" ")[0] ?? "";
    expect(ticketId).toMatch(/^HD-/);
  });

  test("E6S1_agent_claims_the_ticket_from_the_workbench", async ({ page }) => {
    await login(page, "agent1");
    await page.getByLabel("Queue").selectOption("billing");
    await page.getByRole("link", { name: ticketId }).click();

    await expect(page.getByTestId("ticket-assignee")).toContainText("Unassigned");
    await page.getByRole("button", { name: "Claim" }).click();

    await expect(page.getByTestId("ticket-assignee")).not.toContainText("Unassigned");
    await expect(page.getByTestId("ticket-status")).toContainText("IN_PROGRESS");
  });

  test("E6S1_invalid_status_change_shows_the_409_message", async ({ page, browser }) => {
    // StatusControl only offers valid next states (ticket-lifecycle_spec.md
    // Section 2), so the realistic way a 409 reaches the UI is a stale
    // version: two agents open the same ticket, one acts first, and the
    // second's action — built from the page it loaded before that — is
    // rejected with 409 VERSION_CONFLICT.
    const second = await browser.newPage();

    await login(page, "agent1");
    await page.goto(`/tickets/${ticketId}`);
    await expect(page.getByTestId("ticket-status")).toContainText("IN_PROGRESS");

    await login(second, "agent2");
    await second.goto(`/tickets/${ticketId}`);
    await expect(second.getByTestId("ticket-status")).toContainText("IN_PROGRESS");

    await page.getByLabel("Change status").selectOption("PENDING_CUSTOMER");
    await page.getByRole("button", { name: "Update status" }).click();
    await expect(page.getByTestId("ticket-status")).toContainText("PENDING_CUSTOMER");

    // `second` still holds the pre-update version; its own status change
    // now loses with 409 VERSION_CONFLICT, shown through ErrorBanner.
    await second.getByLabel("Change status").selectOption("RESOLVED");
    await second.getByRole("button", { name: "Update status" }).click();
    await expect(second.getByText(/updated by someone else/i)).toBeVisible();

    await second.close();
  });

  test("AC08_customer_reply_on_pending_customer_moves_ticket_to_open", async ({ page }) => {
    await login(page, "customer1");
    await page.goto(`/tickets/${ticketId}`);

    await page.getByLabel("Reply").fill("Here is the requested diagnostic log.");
    await page.getByRole("button", { name: "Send reply" }).click();

    await expect(page.getByText("Here is the requested diagnostic log.")).toBeVisible();

    await login(page, "agent1");
    await page.goto(`/tickets/${ticketId}`);
    await expect(page.getByTestId("ticket-status")).toContainText("OPEN");
  });

  test("E6S1_closed_ticket_is_read_only", async ({ page }) => {
    await login(page, "agent1");
    await page.goto(`/tickets/${ticketId}`);

    // Customer's reply put the ticket back to OPEN; drive it to CLOSED.
    await expect(page.getByTestId("ticket-status")).toContainText("OPEN");
    await page.getByRole("button", { name: "Claim" }).click();
    await expect(page.getByTestId("ticket-status")).toContainText("IN_PROGRESS");

    await page.getByLabel("Change status").selectOption("RESOLVED");
    await page.getByRole("button", { name: "Update status" }).click();
    await expect(page.getByTestId("ticket-status")).toContainText("RESOLVED");

    await page.getByLabel("Change status").selectOption("CLOSED");
    await page.getByRole("button", { name: "Update status" }).click();
    await expect(page.getByTestId("ticket-status")).toContainText("CLOSED");

    await expect(page.getByText("Closed tickets cannot be changed.")).toBeVisible();
    await expect(page.getByRole("button", { name: "Claim" })).toHaveCount(0);
    await expect(page.getByRole("button", { name: "Update status" })).toHaveCount(0);
  });
});
