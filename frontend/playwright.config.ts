import { defineConfig, devices } from "@playwright/test";

/**
 * Playwright config for PM Internship Engine frontend regression suite.
 *
 * The dev server (Next.js on :3000) is started separately via
 * `scripts/start-dev.sh`. We assume it's already running.
 *
 * Run:
 *   npx playwright test                # headless, all tests
 *   npx playwright test --headed       # visible browser
 *   npx playwright test --ui           # interactive UI mode
 *   npx playwright show-report         # open last HTML report
 */
export default defineConfig({
  testDir: "./tests/e2e",
  fullyParallel: false, // sequential — auth state in localStorage would collide
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  workers: 1,
  reporter: [
    ["html", { outputFolder: "playwright-report" }],
    ["list"],
    ["json", { outputFile: "playwright-results.json" }],
  ],
  use: {
    baseURL: "http://localhost:3000",
    trace: "on-first-retry",
    screenshot: "only-on-failure",
    video: "retain-on-failure",
    navigationTimeout: 30000,
    actionTimeout: 15000,
  },
  // Auto-start the Next.js dev server before tests, kill it after.
  // This guarantees the server is up for the entire test run.
  webServer: {
    command: "npm run dev",
    url: "http://localhost:3000/auth/login",
    reuseExistingServer: true,
    timeout: 120_000, // 2 min for first compile
    stdout: "pipe",
    stderr: "pipe",
  },
  projects: [
    {
      name: "chromium",
      testMatch: /.*\.spec\.ts/,
      use: { ...devices["Desktop Chrome"] },
    },
    // Mobile viewport smoke — only run smoke tests on mobile to keep runtime down.
    // mobile-safari (webkit) omitted because the sandbox is missing libgtk-4 and
    // other system libs webkit needs. Add back when running in a full OS env.
    {
      name: "mobile-chrome",
      testMatch: /smoke\.spec\.ts/,
      use: { ...devices["Pixel 7"] },
    },
  ],
});
