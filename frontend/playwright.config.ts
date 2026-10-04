import { existsSync } from "fs";

import { defineConfig, devices } from "@playwright/test";

// E6-S3: snapshots at 375 (mobile), 768 (tablet) and 1280 (desktop) px.
// E6-S5: CI runs this suite against the built app.
//
// In this sandbox the Playwright-managed Chromium download is blocked
// (cdn.playwright.dev is not on the egress allowlist), so point at the
// browser preinstalled under /opt/pw-browsers instead of downloading one,
// when present. A normal CI runner with its own Playwright browsers simply
// won't have this path and falls back to the default.
const sandboxChromium = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome";
const executablePath = existsSync(sandboxChromium) ? sandboxChromium : undefined;

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: false,
  workers: 1,
  reporter: "list",
  // Keep visual baselines at the existing e2e/snapshots/<name>.png paths
  // instead of Playwright's default per-test-file/-project snapshot folder.
  snapshotPathTemplate: "e2e/snapshots/{arg}{ext}",
  expect: {
    toHaveScreenshot: { maxDiffPixelRatio: 0.01 },
  },
  webServer: [
    {
      command: "bash ./e2e/start-backend-with-seed.sh",
      url: "http://localhost:8000/health",
      reuseExistingServer: !process.env.CI,
      timeout: 120_000,
    },
    {
      command: "npm run dev -- --port 5173",
      url: "http://localhost:5173",
      reuseExistingServer: !process.env.CI,
      timeout: 60_000,
    },
  ],
  use: {
    baseURL: process.env.E2E_BASE_URL ?? "http://localhost:5173",
    trace: "on-first-retry",
    launchOptions: { executablePath },
  },
  projects: [
    {
      name: "mobile-375",
      use: { ...devices["Desktop Chrome"], viewport: { width: 375, height: 812 } },
    },
    {
      name: "tablet-768",
      use: { ...devices["Desktop Chrome"], viewport: { width: 768, height: 1024 } },
    },
    {
      name: "desktop-1280",
      use: { ...devices["Desktop Chrome"], viewport: { width: 1280, height: 800 } },
    },
  ],
});
