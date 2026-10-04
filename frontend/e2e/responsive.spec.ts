import { expect, test } from "@playwright/test";

// E6-S3: layouts at 375, 768 and 1280 px (BRD 15). Each Playwright project in
// playwright.config.ts pins one viewport, so this file runs three times and
// leaves one screenshot (snapshot) per breakpoint under test-results/.

async function login(page: import("@playwright/test").Page, username: string): Promise<void> {
  await page.goto("/login");
  await page.getByLabel("Username").fill(username);
  await page.getByLabel("Password").fill("Password123!");
  await page.getByRole("button", { name: "Sign in" }).click();
}

async function hasNoHorizontalScroll(page: import("@playwright/test").Page): Promise<boolean> {
  return page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth + 1);
}

test("E6S3_customer_ticket_list_and_reply_box_have_no_horizontal_scroll_at_375px", async ({
  page,
}) => {
  const size = page.viewportSize();
  test.skip(size?.width !== 375, "this check is only meaningful at the 375 px project");

  await login(page, "customer1");
  await expect(page).toHaveURL(/\/tickets$/);
  expect(await hasNoHorizontalScroll(page)).toBe(true);
  await page.screenshot({ path: "test-results/snapshots/customer-tickets-375.png" });
});

test("E6S3_customer_and_agent_views_render_at_768px", async ({ page }) => {
  const size = page.viewportSize();
  test.skip(size?.width !== 768, "this check is only meaningful at the 768 px project");

  await login(page, "customer1");
  await expect(page.getByRole("heading", { name: "My tickets" })).toBeVisible();
  await page.screenshot({ path: "test-results/snapshots/customer-tickets-768.png" });

  await login(page, "agent1");
  await expect(page.getByRole("heading", { name: "Agent workbench" })).toBeVisible();
  await page.screenshot({ path: "test-results/snapshots/agent-workbench-768.png" });
});

test("E6S3_agent_workbench_renders_in_full_at_1280px", async ({ page }) => {
  const size = page.viewportSize();
  test.skip(size?.width !== 1280, "this check is only meaningful at the 1280 px project");

  await login(page, "agent1");
  await expect(page.getByRole("heading", { name: "Agent workbench" })).toBeVisible();
  await expect(page.getByLabel("Queue")).toBeVisible();
  expect(await hasNoHorizontalScroll(page)).toBe(true);
  await page.screenshot({ path: "test-results/snapshots/agent-workbench-1280.png" });
});
